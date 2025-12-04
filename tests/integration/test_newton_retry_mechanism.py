"""
Integration tests for Newton-Raphson retry mechanism with multiple random guesses.

Tests the feature where NR tries multiple random initial guesses if convergence fails
with the initial guess (Issue: newton-raphson-not-convergence).
"""
import numpy as np
import pytest
from simulator.parser import parse_netlist
from simulator.engine import solve_dc
from simulator.newton import newton_solve


def create_netlist_file(tmp_path, content):
    p = tmp_path / "test.net"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_newton_retry_mechanism_works(tmp_path):
    netlist = """
    2
    V1 1 0 DC 5
    R1 1 2 1000
    D1 2 0
    """
    
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    # Test with default parameters (allows retries)
    result = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[2])
    
    assert result[0] == pytest.approx(0.6368, rel=1e-3)
    assert np.isfinite(result[0])


def test_newton_retry_custom_limits(tmp_path):
    netlist = """
    2
    V1 1 0 DC 3
    R1 1 2 500
    D1 2 0
    """
    
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    # Test with custom limits: 20 iterations per guess, max 10 guesses
    result = solve_dc(
        data, 
        nr_tol=1e-6, 
        v0_vector=None, 
        desired_nodes=[2],
        max_nr_iter=20,
        max_nr_guesses=10
    )
    
    # Should still converge (diode forward voltage ~0.6V)
    assert result[0] == pytest.approx(0.6, rel=0.1)
    assert np.isfinite(result[0])


def test_newton_exhausts_all_attempts():  
    def impossible_mna(x):
        """MNA builder that creates an unsolvable system."""
        n = len(x)
        
        # Create a matrix that will never converge
        G = np.random.randn(n, n) + np.eye(n) * 10
        I = np.random.randn(n) * 1000  # Large random vector
        return G, I
    
    x0 = np.zeros(3)
    
    # Should fail
    with pytest.raises(RuntimeError) as exc_info:
        newton_solve(
            impossible_mna, 
            x0, 
            tol=1e-6, 
            max_iter=5,      # Low N for faster test
            max_guesses=3    # Low M for faster test
        )
    
    # Check error message contains expected information
    error_msg = str(exc_info.value)
    assert "não convergiu" in error_msg.lower()
    assert "tentativas" in error_msg.lower() or "attempts" in error_msg.lower()


def test_newton_first_guess_success(tmp_path):
    netlist = """
    2
    V1 1 0 DC 10
    R1 1 2 1000
    R2 2 0 1000
    """
    
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    # Should converge on first try (linear circuit)
    result = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[2])
    
    # Should be 5V (voltage divider)
    assert result[0] == pytest.approx(5.0, rel=1e-6)


def test_newton_nonlinear_resistor_retry(tmp_path):
    netlist = """
    2
    V1 1 0 DC 10
    R1 1 2 1.0
    N1 2 0 0 0 1 1 2 3 4 4
    """
    
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    result = solve_dc(
        data, 
        nr_tol=1e-6, 
        v0_vector=None, 
        desired_nodes=[2],
        max_nr_iter=30,
        max_nr_guesses=50
    )
    
    # Should converge
    assert np.isfinite(result[0])
    assert 0 <= result[0] <= 10  # Should be on supply voltage range


@pytest.mark.slow
def test_newton_many_retries_eventually_succeeds(tmp_path):
    netlist = """
    3
    V1 1 0 DC 5
    R1 1 2 1000
    D1 2 3 
    R2 3 0 500
    D2 3 0
    """
    
    path = create_netlist_file(tmp_path, netlist)
    data = parse_netlist(path)
    
    result = solve_dc(
        data,
        nr_tol=1e-6,
        v0_vector=None,
        desired_nodes=[2, 3],
        max_nr_iter=50,
        max_nr_guesses=100
    )
    
    # Should converge to physically reasonable voltages
    assert all(np.isfinite(result))
    assert all(0 <= v <= 5 for v in result)
