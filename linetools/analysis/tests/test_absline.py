from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import pytest
import pdb
from astropy import units as u

from linetools.analysis.absline import aodm, log_clm, linear_clm, photo_cross,\
    sum_logN, get_tau0, Wr_from_logN_b
from linetools.lists.linelist import LineList

def test_aodm():
    # Make fake spectrum
    wave = np.linspace(1210, 1220, 100)*u.AA
    npix = wave.size
    fx = np.ones(npix)
    fx[npix//2-5:npix//2+5] = 0.8
    fx[npix//2] = 0.01
    sig = np.ones(npix)*0.1
    wrest = 1215.670*u.AA
    fval = 0.4
    velo = (wave-wrest)/wrest * 3e5*u.km/u.s
    # Operate
    N, sig_N, flag_sat = aodm((velo, fx, sig), (wrest, fval))
    # Test
    assert flag_sat is True
    np.testing.assert_allclose((N.value, sig_N.value),
                               (96652191688169.72, 194151305045168.12))
    assert N.unit == u.cm**-2


def test_logclm():
    obj = type(str('Dummy'), (object,), { str('N'): 1e13, str('sig_N'): 5e12 })
    #
    logN, sig_logN = log_clm(obj)
    np.testing.assert_allclose(logN, 13.)


def test_linearclm():
    obj = type(str('Dummy'), (object,), { str('logN'): 13, str('sig_logN'): 0.2 })
    #
    N, sig_N = linear_clm(obj)
    np.testing.assert_allclose(N.value, 1e13)


def test_photocross():
    phto = photo_cross(1, 1, 14.*u.eV)
    assert phto.unit == u.cm**2
    np.testing.assert_allclose(phto.value, 5.870146496955153e-18)


def test_sumlogn_fail():
    obj1 = dict(flag_N=4)
    obj2 = dict(flag_N=4)
    pytest.raises(ValueError, sum_logN, obj1, obj2)
    #
    obj1 = dict(flag_N=1)
    pytest.raises(ValueError, sum_logN, obj1, obj2)


def test_sumlogn_limit():
    obj1 = dict(flag_N=3, logN=15., sig_logN=99.)
    obj2 = dict(flag_N=1, logN=14., sig_logN=0.3)
    flag_N, logN, sig_logN = sum_logN(obj1, obj2)
    # Test
    assert flag_N == 1
    np.testing.assert_allclose((logN, sig_logN), (obj2['logN'], obj2['sig_logN']))


def test_get_tau0():
    hi_list = LineList('HI')
    lya = hi_list['HI 1215']
    # test float format
    logN = 13.0
    b = 10*u.km/u.s
    tau0 = get_tau0(lya['wrest'], lya['f'], logN, b)
    np.testing.assert_allclose(tau0, 0.75797320235476873, rtol=1e-5)
    # test array format
    logN = [13.0, 13.0, 13.0]
    b = [10., 10, 10]*u.km/u.s
    tau0 = get_tau0(lya['wrest'], lya['f'], logN, b)
    assert len(tau0) == len(logN)
    np.testing.assert_allclose(tau0, 0.75797320235476873, rtol=1e-5)
    # test errors
    with pytest.raises(IOError):
        tau0 = get_tau0(lya['wrest'], lya['f'], logN, b[:2])  # wrong shape for b
    with pytest.raises(IOError):
        tau0 = get_tau0(lya['wrest'], lya['f'], logN[0]*u.km, b[0])  # wrong input for logN (i.e. has units)

def test_Wr_from_logN_b():
    hi_list = LineList('HI')
    lya = hi_list['HI 1215']
    logN = np.linspace(12.0, 22.0, 4)
    b = np.ones_like(logN) * 10 * u.km/u.s
    # test array like
    Wr = Wr_from_logN_b(logN, b, lya['wrest'], lya['f'], lya['gamma'])
    Wr_test = [5.30565005e-03,  1.92538448e-01,  1.60381902e+00, 7.31826938e+01] * u.AA
    np.testing.assert_allclose(Wr, Wr_test, rtol=1e-5)
    # test float like input for logN
    Wr = Wr_from_logN_b(logN[0], b[0], lya['wrest'], lya['f'], lya['gamma'])
    np.testing.assert_allclose(Wr, Wr_test[0], rtol=1e-5)
