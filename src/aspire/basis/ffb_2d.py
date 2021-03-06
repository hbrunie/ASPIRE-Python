import logging
import numpy as np
from numpy import pi
from scipy.special import jv
from scipy.fftpack import ifft, fft

from aspire.nfft import anufft3, nufft3
from aspire.utils.matrix import roll_dim, unroll_dim
from aspire.utils.matlab_compat import m_reshape
from aspire.basis.basis_utils import lgwt
from aspire.basis.fb_2d import FBBasis2D

logger = logging.getLogger(__name__)


class FFBBasis2D(FBBasis2D):
    """
    Define a derived class for Fast Fourier Bessel expansion for 2D images

    The expansion coefficients of 2D images on this basis are obtained by
    a fast method instead of the least squares method.
    The algorithm is described in the publication:
    Z. Zhao, Y. Shkolnisky, A. Singer, Fast Steerable Principal Component Analysis,
    IEEE Transactions on Computational Imaging, 2 (1), pp. 1-12 (2016).​

    """
    def _build(self):
        """
        Build the internal data structure to 2D Fourier-Bessel basis
        """
        logger.info('Expanding 2D image in a frequency-domain Fourier–Bessel'
                    ' basis using the fast method.')

        # set cutoff values
        self.rcut = self.nres / 2
        self.kcut = 0.5

        # get upper bound of zeros, ells, and ks  of Bessel functions
        self._getfbzeros()

        # calculate total number of basis functions
        self.count = self.k_max[0] + sum(2 * self.k_max[1:])

        # generate 1D indices for basis functions
        self._indices = self.indices()

        # precompute the basis functions in 2D grids
        self._precomp = self._precomp()

        # get normalized factors
        self._norms = self.norms()

    def _precomp(self):
        """
        Precomute the basis functions on a polar Fourier grid

        Gaussian quadrature points and weights are also generated.
        The sampling criterion requires n_r=4*c*R and n_theta= 16*c*R.
        
        """
        n_r = int(np.ceil(4 * self.rcut * self.kcut))
        r, w = lgwt(n_r, 0.0, self.kcut)

        radial = np.zeros(shape=(n_r, np.sum(self.k_max)))
        ind_radial = 0
        for ell in range(0, self.ell_max + 1):
            for k in range(1, self.k_max[ell] + 1):
                radial[:, ind_radial] = jv(ell, self.r0[k - 1, ell] * r / self.kcut)
                # NOTE: We need to remove the factor due to the discretization here
                # since it is already included in our quadrature weights
                nrm = 1 / (np.sqrt(np.prod(self.sz))) * self.basis_norm_2d(ell, k)
                radial[:, ind_radial] /= nrm
                ind_radial += 1

        n_theta = np.ceil(16 * self.kcut * self.rcut)
        n_theta = int((n_theta + np.mod(n_theta, 2)) / 2)

        # Only calculate "positive" frequencies in one half-plane.
        freqs_x = m_reshape(r, (n_r, 1)) @ m_reshape(
            np.cos(np.arange(n_theta) * 2 * pi / (2 * n_theta)), (1, n_theta))
        freqs_y = m_reshape(r, (n_r, 1)) @ m_reshape(
            np.sin(np.arange(n_theta) * 2 * pi / (2 * n_theta)), (1, n_theta))
        freqs = np.vstack((freqs_x[np.newaxis, ...], freqs_y[np.newaxis, ...]))

        return {
            'gl_nodes': r,
            'gl_weights': w,
            'radial': radial,
            'freqs': freqs
        }

    def evaluate(self, v):
        """
        Evaluate coefficients in standard 2D coordinate basis from those in FB basis

        :param v: A coefficient vector (or an array of coefficient vectors)
            in FB basis to be evaluated. The first dimension must equal `self.count`.
        :return x: The evaluation of the coefficient vector(s) `x` in standard 2D
            coordinate basis. This is an array whose first two dimensions equal `self.sz`
            and the remaining dimensions correspond to dimensions two and higher of `v`.
        """
        # make should the first dimension of v is self.count
        v, sz_roll = unroll_dim(v, 2)
        v = m_reshape(v, (self.count, -1))

        # get information on polar grids from precomputed data
        n_theta = np.size(self._precomp["freqs"], 2)
        n_r = np.size(self._precomp["freqs"], 1)

        # number of 2D image samples
        n_data = np.size(v, 1)

        # go through  each basis function and find corresponding coefficient
        pf = np.zeros((n_r, 2 * n_theta, n_data), dtype=np.complex)
        mask = self._indices["ells"] == 0

        ind = 0

        idx = ind + np.arange(self.k_max[0])

        pf[:, 0, :] = self._precomp["radial"][:, idx] @ v[mask, ...]

        ind = ind + np.size(idx)

        ind_pos = ind

        for ell in range(1, self.ell_max + 1):
            idx = ind + np.arange(self.k_max[ell])
            idx_pos = ind_pos + np.arange(self.k_max[ell])
            idx_neg = idx_pos + self.k_max[ell]

            v_ell = (v[idx_pos, :] - 1j * v[idx_neg, :]) / 2.0

            if np.mod(ell, 2) == 1:
                v_ell = 1j * v_ell

            pf_ell = self._precomp["radial"][:, idx] @ v_ell
            pf[:, ell, :] = pf_ell

            if np.mod(ell, 2) == 0:
                pf[:, 2 * n_theta - ell, :] = pf_ell.conjugate()
            else:
                pf[:, 2 * n_theta - ell, :] = -pf_ell.conjugate()

            ind = ind + np.size(idx)
            ind_pos = ind_pos + 2 * self.k_max[ell]

        # 1D inverse FFT in the degree of polar angle
        pf = 2 * pi * ifft(pf, axis=1, overwrite_x=True)

        # Only need "positive" frequencies.
        hsize = int(np.size(pf, 1) / 2)
        pf = pf[:, 0:hsize, :]

        for i_r in range(0, n_r):
            pf[i_r, ...] = pf[i_r, ...] * (
                    self._precomp["gl_weights"][i_r] * self._precomp["gl_nodes"][i_r])
        pf = m_reshape(pf, (n_r * n_theta, n_data))

        # perform inverse non-uniformly FFT transform back to 2D coordinate basis
        freqs = m_reshape(self._precomp["freqs"], (2, n_r * n_theta))
        x = np.zeros((self.sz[0], self.sz[1], n_data), dtype=v.dtype)
        for isample in range(0, n_data):
            x[..., isample] = 2*np.real(anufft3(pf[:, isample], 2 * pi * freqs, self.sz))

        # return the x with the first two dimensions of self.sz
        x = roll_dim(x, sz_roll)
        return x

    def evaluate_t(self, x):
        """
        Evaluate coefficient in FB basis from those in standard 2D coordinate basis

        :param x: The coefficient array in the standard 2D coordinate basis to be
            evaluated. The first two dimensions must equal `self.sz`.
        :return v: The evaluation of the coefficient array `v` in the FB basis.
            This is an array of vectors whose first dimension equals `self.count`
            and whose remaining dimensions correspond to higher dimensions of `x`.
        """
        # ensure the first two dimensions with size of self.sz
        x, sz_roll = unroll_dim(x, self.ndim + 1)
        x = m_reshape(x, (self.sz[0], self.sz[1], -1))

        # get information on polar grids from precomputed data
        n_theta = np.size(self._precomp["freqs"], 2)
        n_r = np.size(self._precomp["freqs"], 1)
        freqs = m_reshape(self._precomp["freqs"], new_shape=(2, n_r * n_theta))

        # number of 2D image samples
        n_data = np.size(x, 2)

        pf = np.zeros((n_r*n_theta, n_data), dtype=complex)
        # resamping x in a polar Fourier gird using nonuniform discrete Fourier transform
        for isample in range(0, n_data):
            pf[..., isample] = nufft3(x[..., isample], 2 * pi * freqs, self.sz)
        pf = m_reshape(pf, new_shape=(n_r, n_theta, n_data))

        # Recover "negative" frequencies from "positive" half plane.
        pf = np.concatenate((pf, pf.conjugate()), axis=1)

        # evaluate radial integral using the Gauss-Legendre quadrature rule
        for i_r in range(0, n_r):
            pf[i_r, ...] = pf[i_r, ...] * (
                    self._precomp["gl_weights"][i_r] * self._precomp["gl_nodes"][i_r])

        #  1D FFT on the angular dimension for each concentric circle
        pf = 2 * pi / (2 * n_theta) * fft(pf, 2*n_theta, 1)

        # This only makes it easier to slice the array later.
        v = np.zeros((self.count, n_data), dtype=x.dtype)

        # go through each basis function and find the corresponding coefficient
        ind = 0
        idx = ind + np.arange(self.k_max[0])
        mask = self._indices["ells"] == 0

        v[mask, :] = self._precomp["radial"][:, idx].T @ pf[:, 0, :].real
        v = m_reshape(v, (self.count, -1))
        ind = ind + np.size(idx)

        ind_pos = ind
        for ell in range(1, self.ell_max + 1):
            idx = ind + np.arange(self.k_max[ell])
            idx_pos = ind_pos + np.arange(self.k_max[ell])
            idx_neg = idx_pos + self.k_max[ell]

            v_ell = self._precomp["radial"][:, idx].T @ pf[:, ell, :]

            if np.mod(ell, 2) == 0:
                v_pos = np.real(v_ell)
                v_neg = -np.imag(v_ell)
            else:
                v_pos = np.imag(v_ell)
                v_neg = np.real(v_ell)

            v[idx_pos, :] = v_pos
            v[idx_neg, :] = v_neg

            ind = ind + np.size(idx)

            ind_pos = ind_pos + 2 * self.k_max[ell]

        # return v coefficients with the first dimension of self.count
        v = roll_dim(v, sz_roll)
        return v
