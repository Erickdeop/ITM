# Circuit Simulator (MNA) — OOP

Classes por elemento + polimorfismo. Métodos de integração: BE, FE, TRAP.

## Features

- Modified Nodal Analysis (MNA) with OOP architecture
- Linear elements: R, L, C
- Sources: DC, AC (SIN, PULSE)
- Controlled sources: VCVS, VCCS, CCVS, CCCS
- Nonlinear elements: Diode, Nonlinear Resistor
- Newton-Raphson with multiple random guess retries (handles difficult convergence)
- Integration methods: Backward Euler (BE), Forward Euler (FE), Trapezoidal (TRAP)
- DC and Transient analysis

## Quick Start

```bash
pip install -r requirements.txt
python -m simulator.circuit --netlist ./circuits/example_dc.net --analysis DC --nodes 1
python -m simulator.circuit --netlist ./circuits/example_tran.net --analysis TRAN --total_time 1e-3 --dt 1e-5 --method TRAP --nodes 1
```

## Newton-Raphson Retry Mechanism

For nonlinear circuits that may have convergence difficulties, the simulator implements an automatic retry mechanism:

- **N iterations per guess** (default: 50, typically 20-50)
- **M random guesses maximum** (default: 100)
- Automatically generates new random initial guesses if convergence fails

## Testing

```bash
pytest tests/ -v
```
