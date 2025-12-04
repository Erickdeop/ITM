import numpy as np
from simulator.elements.voltage_source import VoltageSource

def test_voltage_source_augments_mna():
    G = np.zeros((3,3)); I = np.zeros(3)
    v = VoltageSource("V1", 1, 2, dc=5.0)
    G2, I2 = v.stamp_dc(G.copy(), I.copy())
    assert G2.shape == (4,4)
    assert I2.shape == (4,)
    assert G2[1,3] == 1
    assert G2[2,3] == -1
    assert G2[3,1] == 1
    assert G2[3,2] == -1
    assert I2[3] == 5.0
