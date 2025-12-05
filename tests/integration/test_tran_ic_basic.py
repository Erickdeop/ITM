import numpy as np
from simulator.engine import solve_tran
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod


def test_tran_rc_ic_discharge():
    """
    Check if simple RC circuit with initially charged capacitor discharges correctly.
    """
    data = parse_netlist("circuits/example_rc_ic.net")

    t, out, _ = solve_tran(
        data,
        total_time=5e-3,          # ~5 tau to R=1k, C=1e-6
        dt=1e-5,
        nr_tol=1e-6,
        v0_vector=np.zeros(data.max_node + 1),
        desired_nodes=[1],
        method=TimeMethod.BACKWARD_EULER,
    )

    v = out[0]
    assert len(t) == len(v)
    assert len(v) > 10

    assert v[0] > 4.0 # close to 5V (initial charge)
    assert v[-1] < 0.1 # close to 0V (discharged)
    assert v[-1] < v[0] # ensure significant discharge


def test_tran_rl_ic_decay():
    """
    Check if simple RL circuit with initially energized inductor decays correctly.
    """
    data = parse_netlist("circuits/example_rl_ic.net")

    t, out, _ = solve_tran(
        data,
        total_time=5e-4,          # ~5 tau to L=1e-3, R=10 (tau = 1e-4)
        dt=1e-6,
        nr_tol=1e-6,
        v0_vector=np.zeros(data.max_node + 1),
        desired_nodes=[1],
        method=TimeMethod.BACKWARD_EULER,
    )

    v = out[0]
    assert len(t) == len(v)
    assert len(v) > 10

    v0 = v[0]
    assert abs(v0) > 5.0 # close to 10V (initial energy)
    assert abs(v[-1]) < 0.1 # close to 0V (decayed)
    assert abs(v[-1]) < abs(v0) * 0.1 # ensure significant decay
