import pytest
from simulator.circuit import Circuit

def test_dc_vdc_divider_nodes():
    c = Circuit('circuits/vdc_divider.net')
    vals = c.run_dc([1,2])
    assert vals.shape == (2,)
    assert vals[0] == pytest.approx(10.0, rel=1e-6, abs=1e-6)
    assert vals[1] == pytest.approx(5.0, rel=1e-6, abs=1e-6)
