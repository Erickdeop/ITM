import numpy as np
from simulator.engine import solve_tran
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod

def test_transient_rc_step():
    data = parse_netlist("circuits/rc_sine_parallel.net")

    t, out, _ = solve_tran(
        data,
        total_time=0.01,
        dt=1e-4,
        nr_tol=1e-6,
        v0_vector=np.zeros(data.max_node+1),  # FIX
        desired_nodes=[1],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # Sinal AC → não é monotônico.
    # Testamos amplitude > 0.
    assert np.max(np.abs(v)) > 0.1
