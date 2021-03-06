import logging
import numpy as np
from scipy.sparse.linalg import LinearOperator, cg

from aspire.utils import ensure
from aspire.utils.matrix import mdim_mat_fun_conj, roll_dim, unroll_dim
from aspire.utils.matlab_compat import m_reshape
from aspire.basis.basis_utils import num_besselj_zeros

logger = logging.getLogger(__name__)


class Basis:
    """
    Define a base class for expanding 2D particle images and 3D structure volumes

    """
    def __init__(self, size, ell_max=None, dtype=np.float64):
        """
        Initialize an object for the base of basis class

        :param size: The size of the vectors for which to define the basis.
            Currently only square images and cubic volumes are supported.
        :ell_max: The maximum order ell of the basis elements. If no input
            (= None), it will be set to np.Inf and the basis includes all
            ell such that the resulting basis vectors are concentrated
            below the Nyquist frequency (default Inf).
        """
        if ell_max is None:
            ell_max = np.inf

        ndim = len(size)
        nres = size[0]
        self.sz = size
        self.nres = nres
        self.count = 0
        self.ell_max = ell_max
        self.ndim = ndim
        self.dtype = dtype
        if self.dtype != np.float64:
            raise NotImplementedError("Currently only implemented for default double (np.float64) type")

        self._build()

    def _getfbzeros(self):
        """
        Generate zeros of Bessel functions
        """
        # get upper_bound of zeros of Bessel functions
        upper_bound = min(self.ell_max + 1, 2 * self.nres + 1)

        # List of number of zeros
        n = []
        # List of zero values (each entry is an ndarray; all of possibly different lengths)
        zeros = []

        # generate zeros of Bessel functions for each ell
        for ell in range(upper_bound):
            _n, _zeros = num_besselj_zeros(ell + (self.ndim - 2) / 2, self.nres * np.pi / 2)
            if _n == 0:
                break
            else:
                n.append(_n)
                zeros.append(_zeros)

        #  get maximum number of ell
        self.ell_max = len(n) - 1

        #  set the maximum of k for each ell
        self.k_max = np.array(n, dtype=int)

        max_num_zeros = max(len(z) for z in zeros)
        for i, z in enumerate(zeros):
            zeros[i] = np.hstack((z, np.zeros(max_num_zeros - len(z))))

        self.r0 = m_reshape(np.hstack(zeros), (-1, self.ell_max + 1))

    def _build(self):
        """
        Build the internal data structure to represent basis
        """
        raise NotImplementedError('subclasses must implement this')

    def indices(self):
        """
        Create the indices for each basis function
        """
        raise NotImplementedError('subclasses must implement this')

    def _precomp(self):
        """
        Precompute the basis functions at defined sample points
        """
        raise NotImplementedError('subclasses must implement this')

    def norms(self):
        """
        Calculate the normalized factors of basis functions
        """
        raise NotImplementedError('subclasses must implement this')

    def evaluate(self, v):
        """
        Evaluate coefficient vector in basis

        :param v: A coefficient vector (or an array of coefficient vectors)
            to be evaluated. The first dimension must equal `self.count`.
        :return: The evaluation of the coefficient vector(s) `v` for this basis.
            This is an array whose first dimensions equal `self.z` and the
            remaining dimensions correspond to dimensions two and higher of `v`.
        """
        raise NotImplementedError('subclasses must implement this')

    def evaluate_t(self, v):
        """
        Evaluate coefficient in dual basis

        :param v: The coefficient array to be evaluated. The first dimensions
            must equal `self.sz`.
        :return: The evaluation of the coefficient array `v` in the dual
            basis of `basis`.
            This is an array of vectors whose first dimension equals `self.count`
            and whose remaining dimensions correspond to higher dimensions of `v`.
        """
        raise NotImplementedError('Subclasses should implement this')

    def mat_evaluate(self, V):
        """
        Evaluate coefficient matrix in basis

        :param V: A coefficient matrix of size `self.count`-by-
            `self.count` to be evaluated.
        :return: A multidimensional matrix of size `self.sz`-by
            -`self.sz` corresponding to the evaluation of `V` in
            this basis.
        """
        return mdim_mat_fun_conj(V, 1, len(self.sz), self.evaluate)

    def mat_evaluate_t(self, X):
        """
        Evaluate coefficient matrix in dual basis

        :param X: The coefficient array of size `self.sz`-by-`self.sz`
            to be evaluated.
        :return: The evaluation of `X` in the dual basis. This is
            `self.count`-by-`self.count`. matrix.
            If `V` is a matrix of size `self.count`-by-`self.count`,
            `B` is the change-of-basis matrix of `basis`, and `x` is a
            multidimensional matrix of size `basis.sz`-by-`basis.sz`, the
            function calculates V = B' * X * B, where the rows of `B`, rows
            of 'X', and columns of `X` are read as vectorized arrays.
        """
        return mdim_mat_fun_conj(X, len(self.sz), 1, self.evaluate_t)

    def expand(self, x):
        """
        Obtain coefficients in the basis from those in standard coordinate basis

        This is a similar function to evaluate_t but with more accuracy by using
        the cg optimizing of linear equation, Ax=b.

        :param x: An array whose first two or three dimensions are to be expanded
            the desired basis. These dimensions must equal `self.sz`.
        :return : The coefficients of `v` expanded in the desired basis.
            The first dimension of `v` is with size of `count` and the
            second and higher dimensions of the return value correspond to
            those higher dimensions of `x`.

        """
        # ensure the first dimensions with size of self.sz
        x, sz_roll = unroll_dim(x, self.ndim + 1)
        ensure(x.shape[:self.ndim] == self.sz,
               f'First {self.ndim} dimensions of x must match {self.sz}.')

        operator = LinearOperator(shape=(self.count, self.count),
                                  matvec=lambda v: self.evaluate_t(self.evaluate(v)))

        # TODO: (from MATLAB implementation) - Check that this tolerance make sense for multiple columns in v
        tol = 10*np.finfo(x.dtype).eps
        logger.info('Expanding array in basis')

        # number of image samples
        n_data = np.size(x, self.ndim)
        v = np.zeros((self.count, n_data), dtype=x.dtype)

        for isample in range(0, n_data):
            b = self.evaluate_t(x[..., isample])
            # TODO: need check the initial condition x0 can improve the results or not.
            v[..., isample], info = cg(operator, b, tol=tol)
            if info != 0:
                raise RuntimeError('Unable to converge!')

        # return v coefficients with the first dimension of self.count
        v = roll_dim(v, sz_roll)
        return v

    def expand_t(self, v):
        """
        Expand array in dual basis

        This is a similar function to `evaluate` but with more accuracy by
         using the cg optimizing of linear equation, Ax=b.

        If `v` is a matrix of size `basis.ct`-by-..., `B` is the change-of-basis
        matrix of this basis, and `x` is a matrix of size `self.sz`-by-...,
        the function calculates x = (B * B')^(-1) * B * v, where the rows of `B`
        and columns of `x` are read as vectorized arrays.

        :param v: An array whose first dimension is to be expanded in this
            basis's dual. This dimension must be equal to `self.count`.
        :return: The coefficients of `v` expanded in the dual of `basis`. If more
            than one vector is supplied in `v`, the higher dimensions of the return
            value correspond to second and higher dimensions of `v`.

        .. seealso:: expand
        """
        raise NotImplementedError('subclasses should implement this')
