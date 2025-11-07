# Circuit Simulator (MNA) — OOP

Classes por elemento + polimorfismo. Métodos de integração: BE, FE, TRAP.

Quick start:
pip install -r requirements.txt
python -m simulator.circuit --netlist ./circuits/example_dc.net --analysis DC --nodes 1
python -m simulator.circuit --netlist ./circuits/example_tran.net --analysis TRAN --total_time 1e-3 --dt 1e-5 --method TRAP --nodes 1
