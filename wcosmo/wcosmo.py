"""
Core implementation of cosmology functionality.
"""

import numpy as xp

from .taylor import analytic_integral
from .utils import (
    GYR_KM_PER_S_MPC,
    SPEED_OF_LIGHT_KM_PER_S,
    autodoc,
    maybe_jit,
    method_autodoc,
)

__all__ = [
    "FlatwCDM",
    "FlatLambdaCDM",
    "Planck13",
    "Planck15",
    "Planck18",
    "WMAP1",
    "WMAP3",
    "WMAP5",
    "WMAP7",
    "WMAP9",
    "available",
    "comoving_distance",
    "comoving_volume",
    "detector_to_source_frame",
    "differential_comoving_volume",
    "dDLdz",
    "efunc",
    "hubble_distance",
    "hubble_time",
    "inv_efunc",
    "lookback_time",
    "luminosity_distance",
    "source_to_detector_frame",
    "z_at_value",
]


@autodoc
@maybe_jit
def efunc(z, Om0, w0=-1):
    r"""
    Compute the :math:`E(z)` function for a flat wCDM cosmology.

    .. math::

        E(z; \Omega_{{m,0}}, w_0) = \sqrt{{\Omega_{{m,0}} (1 + z)^3
        + (1 - \Omega_{{m,0}}) (1 + z)^{{3(1 + w_0)}}}}

    Parameters
    ----------
    {z}
    {Om0}
    {w0}

    Returns
    -------
    E(z): array_like
        The E(z) function
    """
    zp1 = 1 + z
    return (Om0 * zp1**3 + (1 - Om0) * zp1 ** (3 * (1 + w0))) ** 0.5


@maybe_jit
@autodoc
def inv_efunc(z, Om0, w0=-1):
    """
    Compute the inverse of the E(z) function for a flat wCDM cosmology.

    Parameters
    ----------
    {z}
    {Om0}
    {w0}

    Returns
    -------
    inv_efunc: array_like
        The inverse of the E(z) function
    """
    return 1 / efunc(z, Om0, w0)


@autodoc
def hubble_distance(H0):
    r"""
    Compute the Hubble distance :math:`D_H = c H_0^{{-1}}` in Mpc.

    Parameters
    ----------
    {H0}

    Returns
    -------
    D_H: float
        The Hubble distance in Mpc
    """
    return SPEED_OF_LIGHT_KM_PER_S / H0


@autodoc
def hubble_time(H0):
    r"""
    Compute the Hubble time :math:`t_H = H_0^{{-1}}` in Gyr.

    Parameters
    ----------
    {H0}

    Returns
    -------
    t_H: float
        The Hubble time in Gyr
    """
    return GYR_KM_PER_S_MPC / H0


@autodoc
def hubble_parameter(z, H0, Om0, w0=-1):
    r"""
    Compute the Hubble parameter :math:`H(z)` for a flat wCDM cosmology.

    .. math::

        H(z; H_0, \Omega_{{m,0}}, w_0) = \frac{{d_H(H_0)}}{{E(z; \Omega_{{m,0}}, w_0)}}

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    H(z): array_like
        The Hubble parameter
    """
    return hubble_distance(H0=H0) * inv_efunc(z=z, H0=H0, Om0=Om0, w0=w0)


@maybe_jit
@autodoc
def comoving_distance(z, H0, Om0, w0=-1):
    r"""
    Compute the comoving distance using an analytic integral of the
    Pade approximation.

    .. math::

        d_{{C}} = d_{{H}} \int_{{0}}^{{z}}
        \frac{{dz'}}{{E(z'; \Omega_{{m,0}}, w_0)}}

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    comoving_distance: array_like
        The comoving distance in Mpc
    """
    return analytic_integral(z, Om0, w0) * hubble_distance(H0)


@maybe_jit
@autodoc
def lookback_time(z, H0, Om0, w0=-1):
    r"""
    Compute the lookback time using an analytic integral of the
    Pade approximation.

    .. math::

        t_{{L}} = t_{{H}} \int_{{0}}^{{z}}
        \frac{{dz'}}{{(1 + z')E(z'; \Omega_{{m,0}}, w_0)}}

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    lookback_time: array_like
        The lookback time in km / s / Mpc
    """
    return analytic_integral(z, Om0, w0, zpower=-1) * hubble_time(H0)


@maybe_jit
@autodoc
def absorption_distance(z, Om0, w0=-1):
    r"""
    Compute the absorption distance using an analytic integral of the
    Pade approximation.

    .. math::

        d_{{A}} = \int_{{0}}^{{z}}
        \frac{{dz' (1 + z')^2}}{{E(z'; \Omega_{{m,0}}, w_0)}}

    Parameters
    ----------
    {z}
    {Om0}
    {w0}

    Returns
    -------
    absorption_distance: array_like
        The absorption distance in Mpc
    """
    return analytic_integral(z, Om0, w0, zpower=2)


@maybe_jit
@autodoc
def luminosity_distance(z, H0, Om0, w0=-1):
    r"""
    Compute the luminosity distance using an analytic integral of the
    Pade approximation.

    .. math::

        d_L = (1 + z') d_{{H}} \int_{{0}}^{{z}}
        \frac{{dz'}}{{E(z'; \Omega_{{m,0}}, w_0)}}

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    luminosity_distance: array_like
        The luminosity distance in Mpc
    """
    return (1 + z) * comoving_distance(z, H0, Om0, w0)


@maybe_jit
@autodoc
def dDLdz(z, H0, Om0, w0=-1):
    r"""
    The Jacobian for the conversion of redshift to luminosity distance.

    .. math::

        \frac{{dd_{{L}}}}{{z}} = d_C(z; H_0, \Omega_{{m,0}}, w_0)
        + (1 + z) d_{{H}} E(z; \Omega_{{m, 0}}, w0)

    Here :math:`d_{{C}}` is comoving distance and :math:`d_{{H}}` is the Hubble
    distance.

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    dDLdz: array_like
        The derivative of the luminosity distance with respect to redshift
        in Mpc

    Notes
    -----
    This function does not have a direct analog in the :code:`astropy`
    cosmology objects, but is needed for accounting for expressing
    distributions of redshift as distributions over luminosity distance.
    """
    dC = comoving_distance(z, H0=H0, Om0=Om0, w0=w0)
    Ez_i = inv_efunc(z, Om0=Om0, w0=w0)
    D_H = hubble_distance(H0)
    return dC + (1 + z) * D_H * Ez_i


@autodoc
def z_at_value(func, fval, zmin=1e-4, zmax=100, **kwargs):
    """
    Compute the redshift at which a function equals a given value.

    This follows the approach in :code:`astropy`'s :code:`z_at_value`
    function closely, but uses linear interpolation instead of a root finder.

    Parameters
    ----------
    func: callable
        The function to evaluate, e.g., :code:`Planck15.luminosity_distance`,
        this should take :code:`fval` as the only input.
    fval: float
        The value of the function at the desired redshift
    {zmin}
    {zmax}

    Returns
    -------
    z: float
        The redshift at which the function equals the desired value
    """
    zs = xp.logspace(xp.log10(zmin), xp.log10(zmax), 1000)
    return xp.interp(
        xp.asarray(fval), func(zs, **kwargs), zs, left=zmin, right=zmax, period=None
    )


@maybe_jit
@autodoc
def differential_comoving_volume(z, H0, Om0, w0=-1):
    r"""
    Compute the differential comoving volume element.

    .. math::

        \frac{{dV_{{C}}}}{{dz}} = d_C^2(z; H_0, \Omega_{{m,0}}, w_0) d_H
        E(z; \Omega_{{m, 0}}, w_0)

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    dVc: array_like
        The differential comoving volume element in :math:`\rm{{Gpc}}^3`
    """
    dC = comoving_distance(z, H0, Om0, w0=w0)
    Ez_i = inv_efunc(z, Om0, w0=w0)
    D_H = hubble_distance(H0)
    return dC**2 * D_H * Ez_i


@maybe_jit
@autodoc
def detector_to_source_frame(m1z, m2z, dL, H0, Om0, w0=-1, zmin=1e-4, zmax=100):
    """
    Convert masses and luminosity distance from the detector frame to
    source frame masses and redshift.

    This passes through the arguments to `z_at_value` to compute the
    redshift.

    Parameters
    ----------
    {m1z}
    {m2z}
    {dL}
    {H0}
    {Om0}
    {w0}
    {zmin}
    {zmax}

    Returns
    -------
    m1, m2, z: array_like
        The primary and secondary masses in the source frame and the redshift
    """
    z = z_at_value(luminosity_distance, dL, zmin=zmin, zmax=zmax, H0=H0, Om0=Om0, w0=w0)
    m1 = m1z / (1 + z)
    m2 = m2z / (1 + z)
    return m1, m2, z


@maybe_jit
@autodoc
def source_to_detector_frame(m1, m2, z, H0, Om0, w0=-1):
    """
    Convert masses and redshift from the source frame to the detector frame.

    Parameters
    ----------
    {m1}
    {m2}
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    m1z, m2z, dL: array_like
        The primary and secondary masses in the detector frame and the
        luminosity distance
    """
    dL = luminosity_distance(z, H0, Om0, w0=w0)
    return m1 * (1 + z), m2 * (1 + z), dL


@maybe_jit
@autodoc
def comoving_volume(z, H0, Om0, w0=-1):
    r"""
    Compute the comoving volume out to redshift z.

    .. math::

        V_C = \frac{{4\pi}}{{3}} d^3_C(z; H_0, \Omega_{{m,0}}, w_0)

    Parameters
    ----------
    {z}
    {H0}
    {Om0}
    {w0}

    Returns
    -------
    Vc: array_like
        The comoving volume in :math:`\rm{{Gpc}}^3`
    """
    return 4 / 3 * xp.pi * comoving_distance(z, H0, Om0, w0=w0) ** 3


@autodoc
class FlatwCDM:
    r"""
    Implementation of flat wCDM cosmology to (approximately) match the
    :code:`astropy` API.

    .. math::

        E(z) = \sqrt{{\Omega_{{m,0}} (1 + z)^3
        + (1 - \Omega_{{m,0}}) (1 + z)^{{3(1 + w_0)}}}}

    Parameters
    ----------
    {H0}
    {Om0}
    {w0}
    {zmin}
    {zmax}
    {name}
    {meta}
    """

    def __init__(
        self,
        H0,
        Om0,
        w0,
        *,
        zmin=1e-4,
        zmax=100,
        name=None,
        meta=None,
    ):
        self.H0 = H0
        self.Om0 = Om0
        self.w0 = w0
        self.zmin = zmin
        self.zmax = zmax
        self.name = name
        self.meta = meta

    @property
    def _kwargs(self):
        return {"H0": self.H0, "Om0": self.Om0, "w0": self.w0}

    @property
    def meta(self):
        """
        Meta data for the cosmology to hold additional information, e.g.,
        citation information
        """
        return self._meta

    @meta.setter
    def meta(self, meta):
        if meta is None:
            meta = {}
        self._meta = meta

    @property
    def hubble_distance(self):
        """
        Compute the Hubble distance :math:`D_H = c H_0^{-1}` in Mpc.

        Returns
        -------
        D_H: float
            The Hubble distance in Mpc
        """
        return hubble_distance(self.H0)

    @method_autodoc(alt=luminosity_distance)
    def luminosity_distance(self, z):
        return luminosity_distance(z, **self._kwargs)

    @autodoc
    def dLdH(self, z):
        r"""
        Derivative of the luminosity distance w.r.t. the Hubble distance.

        .. math::

            \frac{{dd_L}}{{dd_H}} = \frac{{d_L}}{{d_H}}

        Parameters
        ----------
        {z}

        Returns
        -------
        array_like:
            The derivative of the luminosity distance w.r.t., the Hubble distance
        """
        return self.luminosity_distance(z) / self.hubble_distance

    @method_autodoc(alt=dDLdz)
    def dDLdz(self, z):
        return dDLdz(z, **self._kwargs)

    @method_autodoc(alt=differential_comoving_volume)
    def differential_comoving_volume(self, z):
        return differential_comoving_volume(z, **self._kwargs)

    @method_autodoc(alt=detector_to_source_frame)
    def detector_to_source_frame(self, m1z, m2z, dL):
        return detector_to_source_frame(
            m1z, m2z, dL, **self._kwargs, zmin=self.zmin, zmax=self.zmax
        )

    @method_autodoc(alt=source_to_detector_frame)
    def source_to_detector_frame(self, m1, m2, z):
        return source_to_detector_frame(m1, m2, z, **self._kwargs)

    @method_autodoc(alt=efunc)
    def efunc(self, z):
        return efunc(z, self.Om0, self.w0)

    @method_autodoc(alt=inv_efunc)
    def inv_efunc(self, z):
        return inv_efunc(z, self.Om0, self.w0)

    @method_autodoc(alt=hubble_parameter)
    def H(self, z):
        return hubble_parameter(z, **self._kwargs)

    @method_autodoc(alt=comoving_distance)
    def comoving_distance(self, z):
        return comoving_distance(z, **self._kwargs)

    @method_autodoc(alt=comoving_volume)
    def comoving_volume(self, z):
        return comoving_volume(z, **self._kwargs)

    @method_autodoc(alt=lookback_time)
    def lookback_time(self, z):
        return lookback_time(z, **self._kwargs)

    @method_autodoc(alt=absorption_distance)
    def absorption_distance(self, z):
        return absorption_distance(z, self.Om0, self.w0)

    @autodoc
    def age(self, z, zmax=1e5):
        """
        Compute the age of the universe at redshift z.

        Parameters
        ----------
        {z}
        zmax: float, optional
            The maximum redshift to consider, default is 1e5

        Returns
        -------
        age: array_like
            The age of the universe in Gyr
        """
        return self.lookback_time(zmax) - self.lookback_time(z)


@autodoc
class FlatLambdaCDM(FlatwCDM):
    r"""
    Implementation of a flat :math:`\Lambda\rm{{CDM}}` cosmology to
    (approximately) match the :code:`astropy` API. This is the same as
    the :code:`FlatwCDM` with :math:`w_0=-1`.

    .. math::

        E(z) = \sqrt{{\Omega_{{m,0}} (1 + z)^3 + (1 - \Omega_{{m,0}})}}

    Parameters
    ----------
    {H0}
    {Om0}
    {zmin}
    {zmax}
    {name}
    {meta}
    """

    def __init__(
        self,
        H0,
        Om0,
        *,
        zmin=1e-4,
        zmax=100,
        name=None,
        meta=None,
    ):
        super().__init__(
            H0=H0, Om0=Om0, w0=-1, zmin=zmin, zmax=zmax, name=name, meta=meta
        )


Planck13 = FlatLambdaCDM(H0=67.77, Om0=0.30712, name="Planck13")
Planck15 = FlatLambdaCDM(H0=67.74, Om0=0.3075, name="Planck15")
Planck18 = FlatLambdaCDM(H0=67.66, Om0=0.30966, name="Planck18")
WMAP1 = FlatLambdaCDM(H0=72.0, Om0=0.257, name="WMAP1")
WMAP3 = FlatLambdaCDM(H0=70.1, Om0=0.276, name="WMAP3")
WMAP5 = FlatLambdaCDM(H0=70.2, Om0=0.277, name="WMAP5")
WMAP7 = FlatLambdaCDM(H0=70.4, Om0=0.272, name="WMAP7")
WMAP9 = FlatLambdaCDM(H0=69.32, Om0=0.2865, name="WMAP9")
available = dict(
    Planck13=Planck13,
    Planck15=Planck15,
    Planck18=Planck18,
    WMAP1=WMAP1,
    WMAP3=WMAP3,
    WMAP5=WMAP5,
    WMAP7=WMAP7,
    WMAP9=WMAP9,
    FlatLambdaCDM=FlatLambdaCDM,
    FlatwCDM=FlatwCDM,
)
