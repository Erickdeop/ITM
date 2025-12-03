import argparse
from simulator.circuit import Circuit

def _cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("--netlist", type=str)
    parser.add_argument("--nr_tol", type=float, default=1e-8)
    parser.add_argument("--nodes", nargs="+", type=int, default=None)
    parser.add_argument("--guide", type=str) # existing .sim file path to print alongsige
    parser.add_argument("--create_sim", action="store_true") # create .sim file after simulating

    
    args = parser.parse_args()

    # Built or open existing circuit
    if args.netlist is None:
        print("Por favor, forneça o caminho para o netlist usando --netlist")
        return
    else:
        circuit = Circuit(args.netlist)

    if __debug__:
        circuit.print()

    # Transient or DC based on netlist settings
    if circuit.data.transient.enabled:
        t, out = circuit.run_tran(
            args.nodes,
            nr_tol=args.nr_tol,
        )

        print("\n==> CIRCUIT TRANSIENT ANALYSIS RESULTS")
        print("Transient points:", len(t))
        for i in range(out.shape[0]):
            if args.nodes is None:
                node = i
            else: 
                node = args.nodes[i]
            print(f"\n- Node {node} first results:", out[i, :10].tolist())
            print(f"- Node {node} last results:", out[i, -10:].tolist())

        ''' SAVE .SIM FILE
        if args.create_sim:
            sim_path = args.netlist.rsplit(".", 1)[0] + ".sim"
            from simulator.simfile import save_sim_file
            save_sim_file(sim_path, t, {f"Node_{node}": out[i] for i, node in enumerate(args.nodes or range(out.shape[0]))})
            print(f".SIM file saved to: {sim_path}")
            '''
        
    else: # data.transient.enabled = false
        print("CIRCUIT DC ANALYSIS RESULTS")
        result = circuit.run_dc(args.nodes, nr_tol=args.nr_tol)
        print("DC Result:", result.tolist())


if __name__ == "__main__":
    _cli()