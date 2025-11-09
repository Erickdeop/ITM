import numpy as np
from simulator.elements.resistor import Resistor

def test_resistor_stamp_dc():
    G = np.zeros((3,3)); I = np.zeros(3)
    r = Resistor(1, 2, 1000.0)
    G2, I2 = r.stamp_dc(G.copy(), I.copy())
    g = 1.0/1000.0
    assert np.isclose(G2[1,1], g)
    assert np.isclose(G2[2,2], g)
    assert np.isclose(G2[1,2], -g)
    assert np.isclose(G2[2,1], -g)
    np.testing.assert_allclose(I2, I)
