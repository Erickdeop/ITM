#### Classe com as regras de cada tipo de componente ####

class Componentes:
    def parse_linha(self, linha, nodemap):
        if linha.startswith("*") or not linha:
            return None
        toks = linha.split()
        tipo = toks[0][0].upper()
        nome = toks[0]
        n1, n2 = toks[1], toks[2]
        valor = float(toks[3])
        ic = float(toks[4].split("=")[1]) if len(toks) > 4 and "IC=" in toks[4].upper() else None

        return {
            "tipo": tipo,
            "nome": nome,
            "n1": nodemap.get(n1),
            "n2": nodemap.get(n2),
            "valor": valor,
            "ic": ic,
        }

    def stamp(self, A, b, elem, h, state, extra_map):
        tipo = elem["tipo"]
        if tipo == "R":
            self.stamp_resistor(A, b, elem)
        elif tipo == "C":
            self.stamp_capacitor(A, b, elem, h, state)
        elif tipo == "L":
            self.stamp_indutor(A, b, elem, h, state, extra_map[elem["nome"]])

    def stamp_resistor(self, A, b, e):
        G = 1 / e["valor"]
        n1, n2 = e["n1"], e["n2"]
        A[n1, n1] += G
        A[n2, n2] += G
        A[n1, n2] -= G
        A[n2, n1] -= G

    def stamp_capacitor(self, A, b, e, h, state):
        if not h: return
        G = e["valor"] / h
        v_prev = state.get(f"V_{e['nome']}", e["ic"] or 0.0)
        n1, n2 = e["n1"], e["n2"]
        A[n1, n1] += G
        A[n2, n2] += G
        A[n1, n2] -= G
        A[n2, n1] -= G
        b[n1] += G * v_prev
        b[n2] -= G * v_prev

    def stamp_indutor(self, A, b, e, h, state, j):
        if not h: h = 1e-12
        i_prev = state.get(f"I_{e['nome']}", e["ic"] or 0.0)
        n1, n2 = e["n1"], e["n2"]
        L = e["valor"]
        A[n1, j] += 1
        A[n2, j] -= 1
        A[j, n1] += -h / L
        A[j, n2] += h / L
        A[j, j] += 1
        b[j] += i_prev
