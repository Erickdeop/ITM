from simulator.circuit import Circuit
from simulator.parser import parse_netlist
def test_dc_simple():
    c = Circuit(parse_netlist('circuits/example_dc.net'))
    ans = c.run_dc([1])
    assert ans.shape == (1,)
