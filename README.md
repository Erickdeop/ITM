# Circuit Simulator (MNA) — OOP

Simulador SPICE educacional implementado em Python utilizando Análise Nodal Modificada (MNA) com arquitetura orientada a objetos.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-76%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Características Principais

- **Análise Nodal Modificada (MNA)** com arquitetura OOP
- **Elementos lineares**: Resistor, Indutor, Capacitor
- **Fontes independentes**: DC, AC com formas de onda SIN e PULSE
- **Fontes controladas**: VCVS (E), VCCS (G), CCVS (H), CCCS (F)
- **Elementos não-lineares**: Diodo, Resistor não-linear
- **Métodos de integração**: Backward Euler (BE), Forward Euler (FE), Trapezoidal (TRAP)
- **Solver não-linear**: Newton-Raphson com retry automático
- **Tipos de análise**: DC e Transiente
- **Visualização**: Gráficos de forma de onda com Matplotlib

## Início Rápido

### Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd ITM

# Opcional, mas é útil ter um ambiente virtual para os requirements
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\\Scripts\\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Exemplos de Uso

```bash
# Análise DC de divisor de tensão
python -m simulator.circuit --netlist ./circuits/vdc_divider.net --analysis DC --nodes 1 2

# Análise transiente de circuito RC com fonte senoidal
python -m simulator.circuit --netlist ./circuits/rc_sine_parallel.net --analysis TRAN --total_time 10e-3 --dt 1e-5 --method TRAP --nodes 1

# Circuito com fonte PULSE
python -m simulator.circuit --netlist ./circuits/pulse.net --analysis TRAN --total_time 5e-3 --dt 1e-6 --method BE --nodes 1
```

## Documentação Completa

A documentação completa do projeto está disponível em formato HTML gerada com Sphinx:

```bash
# Gerar documentação
cd docs
make html

# Abrir no navegador
firefox build/html/index.html
```

A documentação inclui:

- **Visão Geral**: Introdução e características do projeto
- **Instalação**: Guia de configuração do projeto
- **Arquitetura**: Estrutura do código, módulos e padrões de design
- **Uso e Exemplos**: Tutoriais práticos com netlists de exemplo
- **API Reference**: Documentação completa de todas as classes e métodos
- **Testes**: Guia de teste e cobertura
- **Diagrama de Classes**: UML e hierarquia de herança

## Testes

O projeto possui 76 testes (100% passing) organizados em testes unitários e de integração:

```bash
# Executar todos os testes
pytest tests/ -v

# Apenas testes unitários
pytest tests/unit/ -v

# Apenas testes de integração
pytest tests/integration/ -v

# Com relatório de cobertura
pytest tests/ -v --cov=simulator --cov-report=html
```

## Estrutura do Projeto

```
ITM/
├── simulator/          # Código principal
│   ├── parser.py       # Parser de netlists
│   ├── circuit.py      # Interface principal
│   ├── engine.py       # Motor de simulação MNA
│   ├── newton.py       # Solver Newton-Raphson
│   ├── builder.py      # Builder pattern para construção
│   └── elements/       # Classes de elementos
├── circuits/           # Netlists de exemplo
├── tests/              # Suíte de testes
│   ├── unit/           # Testes unitários
│   └── integration/    # Testes de integração
├── docs/               # Documentação Sphinx
│   ├── source/         # Arquivos RST
│   └── build/html/     # HTML gerado
└── requirements.txt    # Dependências Python
```

## Newton-Raphson com Retry Automático

Para circuitos não-lineares com dificuldades de convergência, o simulador implementa:

- **N iterações por tentativa** (padrão: 50)
- **M tentativas com guesses aleatórios** (padrão: 100)
- Geração automática de novos chutes iniciais em caso de falha
- Tolerância configurável (padrão: 1e-6)

## Formato de Netlist

O simulador aceita netlists em formato SPICE simplificado:

```spice
* Exemplo: Divisor de tensão
V1 1 0 DC 10
R1 1 2 1k
R2 2 0 2k
.END
```

Consulte a documentação completa para sintaxe detalhada de todos os elementos.

## Contribuição

Desenvolvido como projeto educacional para a disciplina de Introdução às Técnicas Microeletrônicas (ITM) - UFRJ.

## Licença

Este projeto é distribuído sob licença MIT. Veja o arquivo LICENSE para mais detalhes.
