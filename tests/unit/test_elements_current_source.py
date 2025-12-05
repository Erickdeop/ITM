
import numpy as np
from simulator.elements.current_source import CurrentSource

def test_current_source_stamp_dc():
    I = CurrentSource("I1", 1, 0, dc=2.0, is_ac=False)

    G = np.zeros((2,2))
    Ivec = np.zeros(2)

    G2, I2 = I.stamp_dc(G, Ivec)

    # Current flows from node 1 to node 0, so:
    # - Node 1 loses current: I2[1] should be -2.0
    # - Node 0 gains current: I2[0] should be +2.0
    assert I2[1] == -2.0
    assert I2[0] == 2.0
