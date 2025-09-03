# 🔌 Simulador de Circuitos Elétricos com MNA

Este projeto simula circuitos elétricos contendo resistores, capacitores e indutores usando o método da **Análise Nodal Modificada (MNA)**. Ele lê netlists (arquivos `.net` ou `.txt`) e calcula as tensões e correntes do circuito no ponto DC ou ao longo do tempo (simulação transitória).

---


---

## 📄 Arquivos e suas funções

### `main.py`
> Arquivo principal que roda o programa.

- Carrega uma netlist (`.net` ou `.txt`)
- Realiza a simulação DC e transitória
- Imprime resultados (vetor solução `x`, tensões e correntes)
- Controla o tempo de simulação

---

### `parser/netlist_parser.py`
> Faz o parsing da netlist e cria a lista de componentes.

- Interpreta cada linha do arquivo como um componente (R, C, L)
- Ignora comentários (`*`) e diretivas SPICE (`.TRAN`, `.END`, etc.)
- Retorna uma lista padronizada de componentes (`dict`) e um `NodeMap`

---

### `components/componentes.py`
> Implementa os tipos de componentes e suas estampas no sistema MNA.

Contém a classe `Componentes`, que:

- Define o método `parse_linha(...)` para ler uma linha da netlist
- Possui os métodos:
  - `stamp_resistor(...)`
  - `stamp_capacitor(...)`
  - `stamp_indutor(...)`
- O método `stamp(...)` decide qual dos acima usar com base no tipo (`R`, `C`, `L`)

---

### `core/nodemap.py`
> Mapeia os nomes de nós para índices numéricos.

A classe `NodeMap`:

- Mapeia labels como `"VIN"`, `"GND"`, `"1"`, etc. → inteiros
- Trata o nó `0`, `"GND"` ou `"gnd"` como terra
- Garante que cada nó tenha um índice único para uso nas matrizes

---

### `core/mna_solver.py`
> Constrói e resolve o sistema MNA (A·x = b).

A classe `MNASolver`:

- Monta as matrizes `A` e `b` com base nos componentes
- Aplica as estampas chamando `Componentes.stamp(...)`
- Resolve:
  - `solve_dc()` → simulação em estado estacionário
  - `solve_transient(h, state)` → simulação no tempo (Backward Euler)
- `next_state(...)`: atualiza o estado (capacitores e indutores)

---

---

### `tests/test_parser.py`
> Testes automatizados com `pytest`.

Verifica:

- Se o parser reconhece corretamente componentes
- Se os valores de resistência, capacitância e indutância são corretos
- Se os valores iniciais (`IC=...`) estão sendo lidos

---

## ✅ Funcionalidades Suportadas

- ✅ Resistores (R)
- ✅ Capacitores (C) com IC
- ✅ Indutores (L) com IC
- ✅ Simulação DC
- ✅ Simulação transitória (Backward Euler)
- ✅ Netlists com `.txt` ou `.net`
- ✅ Mapas de nós com inteiros ou labels
- ✅ Estado inicial preservado entre passos

---

## 🚧 Funcionalidades futuras (opcionais)

- [ ] Suporte a fontes de tensão (`V`)
- [ ] Fontes com forma de onda (`PWL`, `SINE`, etc.)
- [ ] Diretivas `.TRAN`, `.AC`, `.DC` automatizadas
- [ ] Interface gráfica (Plotly, Tkinter, etc.)
- [ ] Exportação CSV dos resultados

---

## 🚀 Como usar

1. Instale as dependências:

```bash
pip install numpy pytest



