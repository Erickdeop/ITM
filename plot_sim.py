import argparse
import matplotlib.pyplot as plt
from simulator.circuit import Circuit
from simulator.elements.base import TimeMethod

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

        # plot
        for i, node in enumerate(args.nodes):
            plt.plot(t, out[i], label=f"Node {node}")

        plt.xlabel("Tempo (s)")
        plt.ylabel("Tensão (V)")
        plt.title("Transient Simulation")
        plt.grid(True)
        plt.legend()
        plt.show()

    else:
        print("Nenhuma análise fornecida. Use --tran")

if __name__ == "__main__":
    main()
