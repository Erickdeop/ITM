import argparse
from simulator.parser import parse_netlist
from simulator.circuit import Circuit
from simulator.builder import CircuitBuilder

# --------------------- Add Component to Circuit ----------------------
def add_component (builder: CircuitBuilder):
    print(f"\nADICIONANDO COMPONENTE AO {builder.name}")
    print("TIPO DO COMPONENTE:")
    print("R: Resistor")
    print("C: Capacitor")
    print("L: Indutor")
    type = input(">> ").strip().upper()
    if type == "R":
        a = int(input("Nó positivo: "))
        b = int(input("Nó negativo: "))
        R = float(input("Resistência [ohms]: "))
        builder.add_resistor(a, b, R)

    elif type == "C":
        a = int(input("Nó positivo: "))
        b = int(input("Nó negativo: "))
        C = float(input("Capacitância [F]: "))
        ic = float(input("Tensão inicial [V] (0 se não houver): ") or "0")
        builder.add_capacitor(a, b, C, ic)
    elif type == "L":
        a = int(input("Nó positivo: "))
        b = int(input("Nó negativo: "))
        C = float(input("Indutância [H]: "))
        ic = float(input("Tensão inicial [V] (0 se não houver): ") or "0")
        builder.add_inductor(a, b, C, ic)
    else:
        print("Tipo de componente não reconhecido.")

    # Others

# --------------------- Main Menu ----------------------
def main_menu(circuit_name: str):
    print(f"\nNOVO CIRCUITO: {circuit_name}")
    print("1. Renomear circuito")
    print("2. Adicionar componente")
    print("3. Remover componente")
    print("4. Visualizar componentes")
    print("5. Alterar configurações de simulação")
    print("6. Adicionar arquivo .sim para comparação")
    print("7. Salvar netlist para arquivo .net")
    print("8. Rodar simulação")
    print("0. Sair")

def build_circuit() -> Circuit:
    builder = CircuitBuilder()
    while True:
        main_menu(builder.name)
        choice = input("Escolha uma opção: ").strip()
        # Quit
        if choice == "0":
            print("Saindo do construtor de circuitos.")
            exit(0)
        # Rename
        elif choice == "1":
            new_name = input("Novo nome do circuito: ").strip()
            builder.rename(new_name) if new_name else print("Nome não alterado.")
        # Add component
        elif choice == "2":
            add_component(builder)
        # Remove component
        elif choice == "3":
            print("Á IMPLEMENTAR")
        # View components
        elif choice == "4":
            print(f"\nComponentes do {builder.name}:")
            for elem in builder.elements:
                print("  -", elem)
        # Change simulation settings
        elif choice == "5":
            print("\nCONFIGURAÇÕES ATUAIS DE SIMULAÇÃO")
            type = builder.transient.enabled
            print("Análise:", "Transiente" if type else "DC")
            if type:
                print("Tempo de simulação:", builder.transient.t_stop)
                print("Passo de tempo:", builder.transient.dt)
                print("Método de integração:", builder.transient.method)
                print("Passos internos:", builder.transient.intetnal_steps)

            print("\nALTERAR CONFIGURAÇÕES DE SIMULAÇÃO")
            print ("Deixe em branco para manter o valor atual.")
            new_type = input("Tipo de análise (TRAN/DC): ").strip().upper()

            if new_type == None or new_type == "":
                new_type = type

            if new_type == "TRAN":
                t_stop = float(input("Tempo de simulação (s): "))
                dt = float(input("Passo de tempo (s): "))
                method = input("Método de integração (BE, FE, TRAP): ").strip().upper()
                internal_steps = int(input("Passos internos (0 se nenhum): ") or "0")
                builder.set_transient(
                    t_stop if t_stop else builder.transient.t_stop, 
                    dt if dt else builder.transient.dt, 
                    method if method else builder.transient.method, 
                    internal_steps if internal_steps else builder.transient.intetnal_steps
                    )
            else: # DC
                builder.enable_transient(False)
            
        # Add .sim file
        elif choice == "6":
            print("Á IMPLEMENTAR")
        # Create .net file
        elif choice == "7":
            print("Á IMPLEMENTAR")
            break
        elif choice == "8":
            new_circuit = builder.to_netlist_oop()
            print ("\n\nFINALIZANDO CONSTRUÇÃO DO CIRCUITO...")
            return Circuit(new_circuit)  # Placeholder implementation
        else:
            print("Opção inválida. Tente novamente.")


# --------------------- CLI MANAGER ----------------------
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
        circuit = build_circuit()
        print("Por favor, forneça o caminho para o netlist usando --netlist")
        exit(0)
    else:
        netlist = parse_netlist(args.netlist)
        circuit = Circuit(netlist)

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