import numpy as np
from simulator.engine import solve_tran
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod

def test_transient_rc_step():
    data = parse_netlist("circuits/rc_sine_parallel.net")

    # vetor inicial corrigido
    v0 = np.zeros(data.max_node + 1)

    t, out = solve_tran(
        data,
        total_time=0.01,
        dt=1e-4,
        nr_tol=1e-6,
        v0_vector=v0,
        desired_nodes=[1],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # deve subir
    assert v[10] > v[0]

    # deve aproximar-se de algum valor estável
    assert abs(v[-1] - v[-2]) < 1e-3
