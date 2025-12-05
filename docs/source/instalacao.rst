========================
Instalação e Configuração
========================

Requisitos do Sistema
----------------------

- **Python**: 3.10 ou superior
- **Sistema Operacional**: Linux, macOS ou Windows
- **Memória RAM**: Mínimo 2GB recomendado
- **Espaço em Disco**: ~100MB para instalação completa

Dependências
------------

O projeto requer as seguintes bibliotecas Python:

.. code-block:: text

   numpy
   scipy
   pytest
   pytest-cov
   flake8
   pylint
   matplotlib
   sphinx
   sphinx-rtd-theme
   sphinx-autodoc-typehints
   myst-parser

Instalação Passo a Passo
-------------------------

1. Clonar o Repositório
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/Erickdeop/ITM.git
   cd ITM

2. Criar Ambiente Virtual
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\\Scripts\\activate  # Windows

3. Instalar Dependências
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

4. Verificar Instalação
~~~~~~~~~~~~~~~~~~~~~~~~

Execute os testes para verificar que tudo está funcionando:

.. code-block:: bash

   pytest tests/ -v

Você deve ver algo como:

.. code-block:: text

   ============================== 76 passed in 2.04s ==============================

Configuração do Ambiente
-------------------------

Estrutura de Diretórios
~~~~~~~~~~~~~~~~~~~~~~~~

Após a instalação, seu diretório deve ter a seguinte estrutura:

.. code-block:: text

   ITM/
   ├── simulator/          # Código-fonte principal
   │   ├── elements/       # Classes de elementos
   │   └── plotting/       # Utilitários de plotagem
   ├── circuits/           # Exemplos de netlists
   ├── tests/              # Suite de testes
   │   ├── unit/          # Testes unitários
   │   └── integration/   # Testes de integração
   ├── docs/              # Documentação Sphinx
   ├── main.py            # Interface CLI interativa
   ├── plot.py            # Script de plotagem
   └── requirements.txt   # Dependências

Variáveis de Ambiente (Opcional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para desenvolvimento, você pode configurar:

.. code-block:: bash

   export PYTHONPATH="${PYTHONPATH}:$(pwd)"

Comandos Rápidos de Verificação
--------------------------------

Testar análise DC:

.. code-block:: bash

   python3 -m simulator.circuit --netlist ./circuits/example_dc.net --analysis DC --nodes 1

Testar análise transiente:

.. code-block:: bash

   python3 -m simulator.circuit --netlist ./circuits/example_tran.net --analysis TRAN --total_time 1e-3 --dt 1e-5 --method TRAP --nodes 1

Solução de Problemas Comuns
----------------------------

**Erro: "ModuleNotFoundError"**
   Certifique-se de que o ambiente virtual está ativado e as dependências foram instaladas.

**Erro: "Permission denied"**
   No Linux/macOS, talvez seja necessário usar ``chmod +x`` nos scripts.

**Testes falhando**
   Verifique a versão do Python (deve ser 3.10+) e reinstale as dependências com ``pip install -r requirements.txt --force-reinstall``.

Desinstalação
-------------

Para remover completamente o projeto:

.. code-block:: bash

   deactivate  # Desativar ambiente virtual
   cd ..
   rm -rf ITM  # Linux/macOS
   # ou
   rmdir /s ITM  # Windows
