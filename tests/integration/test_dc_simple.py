from simulator.circuit import Circuit
def test_dc_simple():
    c = Circuit('circuits/example_dc.net')
    ans = c.run_dc([1])
    assert ans.shape == (1,)
