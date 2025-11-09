import numpy as np, pytest
from simulator.circuit import Circuit
from simulator.elements.base import TimeMethod

def test_tran_current_source_resistor_peak_voltage():
    c = Circuit('circuits/r_current_source_ac.net')
    t, out = c.run_tran([1], total_time=5e-3, dt=1e-5, method=TimeMethod.TRAPEZOIDAL)
    v = out[0]
    vmax = float(np.max(np.abs(v[int(0.5*len(v)):])))
    assert 0.9 <= vmax <= 1.1
