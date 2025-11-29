import numpy as np
import pytest
from simulator.parser import parse_netlist
from simulator.engine import solve_dc

def create_netlist_file(tmp_path, content):
    p = tmp_path / "test.net"
    p.write_text(content, encoding="utf-8")
    return str(p)

def test_diode_series_circuit(tmp_path):
    """
    Tests DC convergence of a simple Source-Resistor-Diode circuit.
    V1=5V, R=1k. Expected Vd ~= 0.6368V
    """

    netlist = """
    * Diode test
    V1 1 0 DC 5
    R1 1 2 1000
    D1 2 0
    """

    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    result = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[2])
    
    assert result[0] == pytest.approx(0.6368, rel=1e-3)

def test_nonlinear_resistor_divider(tmp_path):
    """
    Convergência DC de divisor com NLR.
    V=5V, R=1, NLR (PWL). Esperado Vout=2.0V
    """
    netlist = """
    * NLR Divisor
    V1 1 0 DC 5
    R1 1 2 1.0
    N1 2 0 0 0 1 1 2 3 4 4
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    result = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[2])
    
    assert result[0] == pytest.approx(2.0, rel=1e-4)

@pytest.mark.filterwarnings("ignore::RuntimeWarning")
# It is suposed to fail convergence, so we ignore warnings to keep the test output clean.
def test_diode_convergence_failure(tmp_path):
    """
    Optional: Test to ensure the system does not hang/crash
    with bad or extreme parameters (even though Diode has clamp).
    """
    netlist = """
    * Diode convergence failure test
    I1 0 1 DC 1000
    D1 1 0
    """
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    try:
        res = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[1])
        assert np.isfinite(res[0])
    except RuntimeError:
        pass