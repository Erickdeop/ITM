======
Testes
======

Suite de Testes
---------------

O Circuit Simulator MNA possui uma suite abrangente de 76 testes automatizados, divididos em testes unitários e de integração.

Executando os Testes
--------------------

Todos os Testes
~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ -v

Testes Unitários Apenas
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/unit/ -v

Testes de Integração Apenas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/integration/ -v

Com Cobertura de Código
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ --cov=simulator --cov-report=html

O relatório HTML será gerado em ``htmlcov/index.html``.

Estrutura dos Testes
--------------------

.. code-block:: text

   tests/
   ├── unit/                    # Testes unitários (componentes isolados)
   │   ├── test_elements_*.py   # Testes de elementos individuais
   │   ├── test_parser_*.py     # Testes do parser
   │   └── test_*.py            # Outros testes unitários
   └── integration/             # Testes de integração (circuitos completos)
       ├── test_dc_*.py         # Testes de análise DC
       ├── test_tran_*.py       # Testes de análise transiente
       ├── test_nonlinear.py    # Testes de elementos não-lineares
       └── test_*.py            # Outros testes de integração

Testes Unitários
----------------

Objetivo
~~~~~~~~

Validar o comportamento de componentes individuais em isolamento.

Testes de Elementos Lineares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_elements_resistor.py**
  - Valida stamp MNA do resistor
  - Verifica cálculo de condutância

**test_elements_capacitor.py**
  - Testa stamps BE, FE e TRAP
  - Valida condições iniciais de tensão
  - Verifica integração numérica

**test_elements_inductor.py**
  - Testa stamps de integração
  - Valida condições iniciais de corrente
  - Verifica equações companion

**test_elements_voltage_source.py**
  - Testa aumento da matriz MNA
  - Valida stamps DC, AC, SIN, PULSE

**test_elements_current_source.py**
  - Testa stamps de corrente
  - Valida fontes SIN e PULSE
  - Verifica convenção de sinais

Testes de Fontes Controladas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_elements_controlled_sources.py**
  - VCVS: amplificador de tensão
  - VCCS: transcondutância
  - CCVS: transresistência
  - CCCS: espelho de corrente
  - Valida flags MNA

Testes de Elementos Não-Lineares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_elements_nonlinear.py**
  - **Diodo**: Equação de Shockley, clamping de segurança
  - **Resistor não-linear**: Seleção de segmentos PWL

Testes do Parser
~~~~~~~~~~~~~~~~

**test_parser_oop.py**
  - Valida construção de elementos
  - Testa parsing de netlists completas

**test_parser_controlled_sources.py**
  - VCVS, VCCS, CCVS, CCCS
  - Valida parsing de parâmetros

**test_parser_full.py**
  - Testa parsing de todos os tipos de elementos

Testes de Fontes Variáveis no Tempo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_pulse_sin_sources.py**
  - Testa fontes DC, AC
  - Valida forma de onda SIN (offset, amplitude, freq, delay, damping, phase)
  - Valida forma de onda PULSE (rise, fall, width, period)

**test_current_source_sin_pulse.py**
  - Testa fontes de corrente SIN
  - Testa fontes de corrente PULSE
  - Valida periodicidade e amortecimento

Testes de Integração
---------------------

Objetivo
~~~~~~~~

Validar o comportamento de circuitos completos em análises DC e transiente.

Testes de Análise DC
~~~~~~~~~~~~~~~~~~~~~

**test_dc_simple.py**
  - Circuitos resistivos simples
  - Valida solução de divisores de tensão

**test_dc_vdc_divider.py**
  - Divisor de tensão com múltiplos nós
  - Verifica tensões nodais

Testes de Análise Transiente
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_transient_rc_basic.py**
  - Resposta ao degrau de circuito RC
  - Valida constante de tempo τ = RC

**test_tran_rc_sine.py**
  - Resposta senoidal de circuito RC
  - Valida amplitude e defasagem

**test_tran_ic_basic.py**
  - Condições iniciais de capacitores (descarga)
  - Condições iniciais de indutores (decaimento)

**test_tran_current_source.py**
  - Fontes de corrente em análise transiente
  - Valida pico de tensão em resistor

Testes de Circuitos Não-Lineares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_nonlinear.py**
  - Circuito com diodo em série
  - Divisor com resistor não-linear
  - Testa falha de convergência intencional

**test_newton_retry_mechanism.py**
  - Valida mecanismo de retry do Newton-Raphson
  - Testa limites personalizados de iterações
  - Verifica esgotamento de tentativas
  - Valida sucesso na primeira tentativa
  - Testa retry com resistor não-linear
  - Valida convergência eventual com muitas tentativas

Testes de Fontes de Corrente SIN/PULSE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_current_source_sin_pulse.py (integração)**
  - SIN com oscilação
  - PULSE com níveis alto/baixo
  - Parser de sintaxe SIN e PULSE

Testes de Fontes Controladas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**test_controlled_sources.py**
  - Amplificador de tensão (VCVS)
  - Espelho de corrente (CCCS)
  - Transcondutância (VCCS)
  - Transresistência (CCVS)
  - Amplificador inversor
  - Controle zero

Testes de AmPop
~~~~~~~~~~~~~~~

**test_ampop.py**
  - Parser de OpAmp ideal
  - Follower DC com virtual short

Cobertura de Código
--------------------

Áreas com Alta Cobertura
~~~~~~~~~~~~~~~~~~~~~~~~

- **Elementos lineares**: ~95%
- **Parser**: ~90%
- **Engine (DC/Transient)**: ~85%
- **Newton-Raphson**: ~90%

Áreas com Cobertura Limitada
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Interface CLI interativa**: ~60% (main.py)
- **Plotting**: ~70%
- **MOSFET**: 0% (não implementado)

Casos de Teste Importantes
---------------------------

Convergência Difícil
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_newton_retry_mechanism_works():
       # Circuito difícil que requer múltiplas tentativas
       # Valida que o retry funciona

Condições Iniciais
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_tran_rc_ic_discharge():
       # Capacitor com carga inicial
       # Valida descarga exponencial

Elementos Não-Lineares
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_diode_series_circuit():
       # Circuito com diodo
       # Valida tensão de junção e corrente

Periodicidade
~~~~~~~~~~~~~

.. code-block:: python

   def test_current_source_pulse_periodicity():
       # Fonte PULSE com período
       # Valida repetição do sinal

Executando Testes Específicos
------------------------------

Teste Individual
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/unit/test_elements_resistor.py::test_resistor_stamp_dc -v

Teste por Marcador
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest -m unit -v     # Apenas unitários
   pytest -m integration -v  # Apenas integração

Teste com Saída Detalhada
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/ -vv --tb=long

Continuous Integration
----------------------

Os testes são executados automaticamente via GitHub Actions em cada push e pull request.

**Arquivo**: ``.github/workflows/cicd.yml``

.. code-block:: yaml

   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
         - name: Install dependencies
           run: pip install -r requirements.txt
         - name: Run tests
           run: pytest tests/ -v

Boas Práticas
-------------

1. **Escrever testes antes de implementar** (TDD quando possível)
2. **Um assert por teste** quando viável
3. **Nomes descritivos** para funções de teste
4. **Fixtures** para setup compartilhado
5. **Mocks** apenas quando necessário
6. **Tolerâncias numéricas** com ``pytest.approx()``

Exemplo de Teste
----------------

.. code-block:: python

   import pytest
   import numpy as np
   from simulator.elements.resistor import Resistor

   def test_resistor_stamp_dc():
       r = Resistor(a=1, b=0, R=1000.0)
       G = np.zeros((2, 2))
       I = np.zeros(2)
       
       G_new, I_new = r.stamp_dc(G, I)
       
       # Verificações
       assert G_new[1, 1] == pytest.approx(1e-3)  # 1/R
       assert G_new[1, 0] == pytest.approx(-1e-3)
       assert np.array_equal(I_new, I)  # I não muda
