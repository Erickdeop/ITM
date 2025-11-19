
import numpy as np
from simulator.elements.current_source import CurrentSource

def test_current_source_stamp_dc():
    I = CurrentSource(1, 0, dc=2.0, is_ac=False)

    G = np.zeros((2,2))
    Ivec = np.zeros(2)

    G2, I2 = I.stamp_dc(G, Ivec)

    assert I2[1] == 2.0
    assert I2[0] == -2.0
