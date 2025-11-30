import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from simulator.circuit import Circuit
from simulator.elements.base import TimeMethod


#  Detectar arquivo .sim referente ao netlisth
def find_sim_file(netlist_path):
    # Caminho absoluto da netlist
    abs_net = os.path.abspath(netlist_path)
    base, _ = os.path.splitext(abs_net)
    sim_path = base + ".sim"

    if os.path.exists(sim_path):
        print(f"[DEBUG] .sim encontrado em: {sim_path}")
        return sim_path

    print(f"[DEBUG] .sim NÃO encontrado. netlist={abs_net}, esperado={sim_path}")
    return None

# ------------------------------------------------------------
# 2) Ler arquivo .sim
# ------------------------------------------------------------
from io import StringIO
import numpy as np

def load_sim_file(path):
    print(f"[DEBUG] Processando .sim bruto: {path}")

    numeric_lines = []
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue  # pula linha vazia

            # tenta interpretar a primeira coluna como float
            parts = line.split()
            try:
                float(parts[0])
            except ValueError:
                # não é linha numérica (provavelmente cabeçalho ou texto) → ignora
                continue

            numeric_lines.append(line)

    if not numeric_lines:
        print(f"[PLOT] Nenhuma linha numérica encontrada em {path}")
        return None, None

    # monta um "arquivo" em memória só com as linhas numéricas
    buffer = StringIO("\n".join(numeric_lines))

    try:
        data = np.loadtxt(buffer)
    except Exception as e:
        print(f"[PLOT] erro ao converter dados numéricos de {path}: {e}")
        return None, None

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # primeira coluna = tempo
    time = data[:, 0]

    # demais colunas = variáveis
    variables = {
        f"SIM_col{i}": data[:, i]
        for i in range(1, data.shape[1])
    }

    print(
        f"[DEBUG] .sim carregado de {path}: "
        f"{data.shape[0]} pontos, {data.shape[1]-1} variáveis"
    )
    return time, variables


#Função genérica de plot
def plot_all(time, results_dict, time_sim=None, sim_results=None):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    ax_py, ax_sim = axes

    #grafico de simulacao python
    for name, values in results_dict.items():
        ax_py.plot(time, values, label=f"PY: {name}")

    ax_py.set_title("Simulação Python")
    ax_py.set_xlabel("Tempo (s)")
    ax_py.set_ylabel("Tensão / Valor")
    ax_py.grid(True)
    ax_py.legend()

    #arquivo .sim
    if sim_results is not None:
        for name, values in sim_results.items():
            ax_sim.plot(time_sim, values, "--", label=f"SIM: {name}")

        ax_sim.set_title("Simulação .SIM (referência)")
        ax_sim.set_xlabel("Tempo (s)")
        ax_sim.grid(True)
        ax_sim.legend()
    else:
        ax_sim.set_title("Nenhum arquivo .SIM encontrado")
        ax_sim.set_axis_off()

    plt.tight_layout()
    plt.show()


#integrando plots
def main():
    parser = argparse.ArgumentParser(description="Plot results of circuit simulation")

    parser.add_argument("--net", required=True, help="Caminho da netlist")
    parser.add_argument("--nodes", nargs="+", type=int, default=[1], help="Nós a serem plotados")

    parser.add_argument(
        "--tran",
        nargs=2,
        metavar=("TSTOP", "DT"),
        help="Executa análise transiente: Tstop dt"
    )

    parser.add_argument("--method", choices=["BE", "FE", "TRAP"], default="TRAP")

    args = parser.parse_args()

    # método numérico
    method_map = {
        "BE": TimeMethod.BACKWARD_EULER,
        "FE": TimeMethod.FORWARD_EULER,
        "TRAP": TimeMethod.TRAPEZOIDAL,
    }
    method = method_map[args.method]

    # carregar circuito
    ckt = Circuit(args.net)

    # se pediu transient
    if args.tran:
        total_time = float(args.tran[0])
        dt = float(args.tran[1])

        t, out = ckt.run_tran(
            desired_nodes=args.nodes,
            total_time=total_time,
            dt=dt,
            method=method
        )

        # ---- preparar dict para plot genérico ----
        python_results = {
            f"Node {node}": out[i]
            for i, node in enumerate(args.nodes)
        }

        # ---- procurar .sim correspondente ----
        sim_file = find_sim_file(args.net)
        time_sim = None
        sim_results = None

        if sim_file:
            print(f"Arquivo .sim encontrado: {sim_file}")
            time_sim, sim_results = load_sim_file(sim_file)

        # ---- plot conjunto ----
        plot_all(t, python_results, time_sim, sim_results)

    else:
        print("Nenhuma análise fornecida. Use --tran")


if __name__ == "__main__":
    main()
