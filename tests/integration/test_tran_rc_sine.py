import numpy as np, pytest
from simulator.circuit import Circuit
from simulator.elements.base import TimeMethod

def test_tran_rc_sine_parallel_amplitude():
    c = Circuit('circuits/rc_sine_parallel.net')
    t, out = c.run_tran([1])
    v = out[0]
    vmax = float(np.max(np.abs(v[int(0.5*len(v)):])))
    assert 0.9 <= vmax <= 1.1
