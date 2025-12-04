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
    
    # Check dimensions
    assert G_new.shape == (6, 6)
    assert I_new.shape == (6,)
    
    # Check control current KCL stamps
    assert G_new[3, 4] == 1.0   # Node c gets +i_control
    assert G_new[0, 4] == -1.0  # Node d (0) gets -i_control
    
    # Check output current KCL stamps
    assert G_new[1, 5] == 1.0   # Node a gets +i_output
    assert G_new[2, 5] == -1.0  # Node b gets -i_output
    
    # Check control constraint equation (row 4): v_c - v_d = 0
    assert G_new[4, 3] == 1.0   # +v_c
    assert G_new[4, 0] == -1.0  # -v_d
    
    # Check output constraint equation (row 5): v_a - v_b - rm*i_control = 0
    assert G_new[5, 1] == 1.0      # +v_a
    assert G_new[5, 2] == -1.0     # -v_b
    assert G_new[5, 4] == -1000.0  # -rm*i_control


def test_controlled_sources_mna_flags():
    assert VCVS(1, 0, 2, 0, 5.0).is_mna is True
    assert CCCS(1, 0, 2, 0, 3.0).is_mna is True
    assert VCCS(1, 0, 2, 0, 0.01).is_mna is False
    assert CCVS(1, 0, 2, 0, 100.0).is_mna is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
