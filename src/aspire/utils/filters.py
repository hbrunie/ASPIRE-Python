import inspect
import numpy as np
from scipy.interpolate import RegularGridInterpolator

from aspire.utils import ensure
from aspire.utils.em import voltage_to_wavelength
from aspire.utils.coor_trans import grid_2d
from aspire.utils.matlab_compat import m_reshape
from aspire.utils.blk_diag_matrix import filter_to_fb_mat


class Filter:
    def __init__(self, dim=2, radial=False):
        self.dim = dim
        self.radial = radial
        self._scale = 1  # If needed, modified through the scale() method

    def __mul__(self, other):
        return MultiplicativeFilter(self, other)

    def evaluate(self, omega):
        """
        Evaluate the filter at specified frequencies.
        :param omega: A vector of size n (for 1d filters), or an array of size 2-by-n, representing the spatial
            frequencies at which the filter is to be evaluated. These are normalized so that pi is equal to the Nyquist
            frequency.
        :return: The value of the filter at the specified frequencies.
        """
        if omega.ndim == 1:
            ensure(self.radial, f'Cannot evaluate a non-radial filter on 1D input array.')
        elif omega.ndim == 2:
            ensure(omega.shape[0] == self.dim, f'Omega must be of size {self.dim} x n')

        if self.radial:
            if omega.ndim > 1:
                omega = np.sqrt(np.sum(omega ** 2, axis=0))
            omega, idx = np.unique(omega, return_inverse=True)
            omega = np.vstack((omega, np.zeros_like(omega)))

        h = self._evaluate(omega)

        if self.radial:
            h = np.take(h, idx)

        return h

    def _evaluate(self, omega):
        raise NotImplementedError('Subclasses should implement this method')

    def fb_mat(self, fbasis):
        """
        Represent the filter in FB basis matrix
        """
        return filter_to_fb_mat(self.evaluate, fbasis)

    def scale(self, c):
        """
        Scale filter by a constant factor
        :param c: The scaling factor. For c < 1, it dilates the filter(s) in frequency, while for c > 1,
            it compresses (default 1).
        :return: On return, attributes of the calling object are properly adjusted in place to effect scaling.
        """
        raise NotImplementedError('Subclasses should implement this method')

    def evaluate_grid(self, L, *args, **kwargs):
        grid2d = grid_2d(L)
        omega = np.pi * np.vstack((grid2d['x'].flatten('F'), grid2d['y'].flatten('F')))
        h = self.evaluate(omega, *args, **kwargs)

        h = m_reshape(h, grid2d['x'].shape)

        return h


class FunctionFilter(Filter):
    """
    A Filter object that is instantiated directly using a 1D or 2D function, which is then directly used for evaluating
    the filter.
    """
    def __init__(self, f, dim=None):
        n_args = len(inspect.signature(f).parameters)
        assert n_args in (1, 2), "Only 1D or 2D functions are supported"

        assert dim in (None, 1, 2), "Only 1D or 2D dimensions are supported"
        dim = dim or n_args

        self.f = f  # will be used directly in this Filter's evaluate method
        # Note: The function may well be radial from the caller's perspective, but we won't be applying it in a radial
        # manner if the function we were initialized from expected 2 arguments
        # (i.e. at runtime, we will still expect the incoming omega values to have x and y components).
        super().__init__(dim=dim, radial=dim > n_args)

    def _evaluate(self, omega):
        return self.f(*omega)


class PowerFilter(Filter):
    """
    A Filter object that is composed of a regular `Filter` object, but evaluates it to a specified power.
    """
    def __init__(self, filter, power=1):
        self._filter = filter
        self._power = power
        super().__init__(dim=filter.dim, radial=filter.radial)

    def _evaluate(self, omega):
        return self._filter.evaluate(omega) ** self._power


class MultiplicativeFilter(Filter):
    """
    A Filter object that returns the product of the evaluation of its individual filters
    """
    def __init__(self, *args):
        super().__init__(
            dim=args[0].dim,
            radial=all(c.radial for c in args)
        )
        self._components = args

    def _evaluate(self, omega):
        res = 1
        for c in self._components:
            res *= c.evaluate(omega)
        return res


class ArrayFilter(Filter):
    def __init__(self, xfer_fn_array):
        """
        A Filter corresponding to the filter with the specified transfer function.
        :param xfer_fn_array: The transfer function of the filter in the form of an array of one or two dimensions.
        """
        dim = xfer_fn_array.ndim
        ensure(dim in (1, 2), "Only dimensions 1 and 2 supported.")

        super().__init__(dim=dim, radial=False)

        # sz is assigned before we do anything with xfer_fn_array
        self.sz = xfer_fn_array.shape

        # The following code, though superficially different from the MATLAB code its copied from,
        # results in the same behavior.
        # TODO: This could use documentation - very unintuitive!
        if dim == 1:
            # If we have a vector of even length, then append the first element to the last
            if xfer_fn_array.shape[0] % 2 == 0:
                xfer_fn_array = np.concatenate((xfer_fn_array, np.array([xfer_fn_array[0]])))
        elif dim == 2:
            # If we have a 2d array with an even number of rows, append the first row reversed at the bottom
            if xfer_fn_array.shape[0] % 2 == 0:
                xfer_fn_array = np.vstack((xfer_fn_array, xfer_fn_array[0, ::-1]))
            # If we have a 2d array with an even number of columns, append the first column reversed at the right
            if xfer_fn_array.shape[1] % 2 == 0:
                xfer_fn_array = np.hstack((xfer_fn_array, xfer_fn_array[::-1, 0][:, np.newaxis]))

        self.xfer_fn_array = xfer_fn_array

    def _evaluate(self, omega):
        sz = self.sz
        # TODO: This part could do with some documentation - not intuitive!
        omega = omega / self._scale
        temp = np.array(sz)[:, np.newaxis]
        omega = (omega/(2 * np.pi)) * temp
        omega += np.floor(temp/2) + 1

        # Emulating the behavior of interpn(V,X1q,X2q,X3q,...) in MATLAB
        _input_pts = tuple(list(range(1, x+1)) for x in self.xfer_fn_array.shape)
        interpolator = RegularGridInterpolator(
            _input_pts,
            self.xfer_fn_array,
            bounds_error=False,
            fill_value=0
        )
        result = interpolator(
            # Split omega into input arrays and stack depth-wise because that's how
            # the interpolator wants it
            np.dstack(
                np.split(omega, len(sz))
            )
        )

        # Result is 1 x np.prod(sz) in shape; convert to a 1-d vector
        result = np.squeeze(result, 0)
        return result

    def scale(self, c):
        self._scale *= c


class ScalarFilter(Filter):
    def __init__(self, dim=2, value=1):
        super().__init__(dim=dim, radial=True)
        self.value = value

    def __repr__(self):
        return f'Scalar Filter (dim={self.dim}, value={self.value})'

    def _evaluate(self, omega):
        return self.value * np.ones_like(omega)

    def scale(self, c):
        # TODO: Is this a bug?
        pass


class ZeroFilter(ScalarFilter):
    def __init__(self, dim=2):
        super().__init__(dim=dim, value=0)


class IdentityFilter(ScalarFilter):
    def __init__(self, dim=2):
        super().__init__(dim=dim, value=1)


class CTFFilter(Filter):
    def __init__(self, pixel_size=10, voltage=200, defocus_u=15000, defocus_v=15000, defocus_ang=0, Cs=2.26,
                 alpha=0.07, B=0):
        """
        A CTF (Contrast Transfer Function) Filter

        :param pixel_size:  Pixel size in angstrom
        :param voltage:     Electron voltage in kV
        :param defocus_u:   Defocus depth along the u-axis in angstrom
        :param defocus_v:   Defocus depth along the v-axis in angstrom
        :param defocus_ang: Angle between the x-axis and the u-axis in radians
        :param Cs:          Spherical aberration constant
        :param alpha:       Amplitude contrast phase in radians
        :param B:           Envelope decay in inverse square angstrom (default 0)
        """
        super().__init__(dim=2, radial=defocus_u == defocus_v)
        self.pixel_size = pixel_size
        self.voltage = voltage
        self.wavelength = voltage_to_wavelength(self.voltage)
        self.defocus_u = defocus_u
        self.defocus_v = defocus_v
        self.defocus_ang = defocus_ang
        self.Cs = Cs
        self.alpha = alpha
        self.B = B

        self.defocus_mean = 0.5 * (self.defocus_u + self.defocus_v)
        self.defocus_diff = 0.5 * (self.defocus_u - self.defocus_v)

    def _evaluate(self, omega):
        om_x, om_y = np.vsplit(omega / (2 * np.pi * self.pixel_size), 2)

        eps = np.finfo(np.pi).eps
        ind_nz = (np.abs(om_x) > eps) | (np.abs(om_y) > eps)
        angles_nz = np.arctan2(om_y[ind_nz], om_x[ind_nz])
        angles_nz -= self.defocus_ang

        defocus = np.zeros_like(om_x)
        defocus[ind_nz] = self.defocus_mean + self.defocus_diff * np.cos(2 * angles_nz)

        c2 = -np.pi * self.wavelength * defocus
        c4 = 0.5 * np.pi * (self.Cs * 1e7) * self.wavelength**3

        r2 = om_x**2 + om_y**2
        r4 = r2**2
        gamma = c2*r2 + c4*r4
        h = np.sqrt(1 - self.alpha**2) * np.sin(gamma) - self.alpha * np.cos(gamma)

        if self.B:
            h *= np.exp(-self.B * r2)

        return h.squeeze()

    def scale(self, c=1):
        self.pixel_size *= c


class RadialCTFFilter(CTFFilter):
    def __init__(self, pixel_size=10, voltage=200, defocus=15000, Cs=2.26, alpha=0.07, B=0):
        super().__init__(pixel_size=pixel_size, voltage=voltage, defocus_u=defocus, defocus_v=defocus, defocus_ang=0,
                         Cs=Cs, alpha=alpha, B=B)
