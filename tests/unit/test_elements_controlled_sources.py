import pytest
import numpy as np
from simulator.elements.controlled_sources import VCVS, CCCS, VCCS, CCVS


def test_vcvs_stamp_basic():
    G = np.zeros((4, 4))
    I = np.zeros(4)
    
    vcvs = VCVS(a=1, b=2, c=3, d=0, gain=10.0)
    G_new, I_new = vcvs.stamp_dc(G, I)
    
    assert G_new.shape == (5, 5)
    assert G_new[1, 4] == 1.0
    assert G_new[4, 3] == 10.0


def test_cccs_stamp_basic():
    G = np.zeros((4, 4))
    I = np.zeros(4)
    
    cccs = CCCS(a=1, b=2, c=3, d=0, gain=5.0)
    G_new, I_new = cccs.stamp_dc(G, I)
    
    assert G_new.shape == (5, 5)
    assert G_new[1, 4] == 5.0


def test_vccs_stamp_basic():
    G = np.zeros((4, 4))
    I = np.zeros(4)
    
    vccs = VCCS(a=1, b=2, c=3, d=0, gm=0.01)
    G_new, I_new = vccs.stamp_dc(G, I)
    
    assert G_new.shape == (4, 4)
    assert G_new[1, 3] == 0.01


def test_ccvs_stamp_basic():
    G = np.zeros((4, 4))
    I = np.zeros(4)
    
    ccvs = CCVS(a=1, b=2, c=3, d=0, rm=1000.0)
    G_new, I_new = ccvs.stamp_dc(G, I)
    
    assert G_new.shape == (6, 6)
    assert G_new[5, 5] == 1000.0


def test_controlled_sources_mna_flags():
    assert VCVS(1, 0, 2, 0, 5.0).is_mna is True
    assert CCCS(1, 0, 2, 0, 3.0).is_mna is True
    assert VCCS(1, 0, 2, 0, 0.01).is_mna is False
    assert CCVS(1, 0, 2, 0, 100.0).is_mna is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
