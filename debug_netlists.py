import os
import traceback
from simulator.parser import parse_netlist
from simulator.engine import solve_dc, solve_tran
from simulator.elements.base import TimeMethod
import numpy as np

CIRCUIT_DIR = "circuits"

def test_netlist(path):
    print("\n============================")
    print(f" TESTANDO: {path}")
    print("============================")

    try:
        data = parse_netlist(path)
        print("✔️  Parser OK")
    except Exception as e:
        print("❌ Erro no parser")
        print(e)
        return

    # ============================================================
    # TESTE DC
    # ============================================================
    try:
        desired = [1] if data.max_node >= 1 else [0]
        out = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=desired)
        print(f"✔️  DC OK → V(node {desired}) = {out}")
    except Exception as e:
        print("❌ Erro na análise DC:")
        traceback.print_exc()

    # ============================================================
    # TESTE TRANSIENTE
    # ============================================================
    try:
        t, o = solve_tran(
            data,
            total_time=1e-3,
            dt=1e-5,
            nr_tol=1e-6,
            v0_vector=np.zeros(data.max_node + 1),
            desired_nodes=[1] if data.max_node >= 1 else [0],
            method=TimeMethod.TRAPEZOIDAL
        )
        print(f"✔️  TRANSIENTE OK → últimos valores: {o[:,-1]}")
    except Exception as e:
        print("❌ Erro na análise transiente:")
        traceback.print_exc()


def main():
    print("🔍 Procurando netlists em:", CIRCUIT_DIR)
    files = [f for f in os.listdir(CIRCUIT_DIR) if f.endswith(".sim")]

    if not files:
        print("⚠️ Nenhum arquivo .sim encontrado")
        return

    for f in files:
        test_netlist(os.path.join(CIRCUIT_DIR, f))

    print("\n======================================")
    print(" Testes finalizados.")
    print("======================================")

if __name__ == "__main__":
    main()
