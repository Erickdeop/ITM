#!/bin/bash
# Script para gerar comparações de todos os circuitos com arquivos .sim

if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "✓ Usando virtual environment: .venv/"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
    echo "✓ Usando virtual environment: venv/"
elif [ -n "$VIRTUAL_ENV" ]; then
    PYTHON_CMD="python"
    echo "✓ Usando virtual environment ativo: $VIRTUAL_ENV"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "⚠ Usando Python do sistema (considere usar um virtual environment)"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "⚠ Usando Python3 do sistema (considere usar um virtual environment)"
else
    echo "❌ Erro: Python não encontrado. Instale Python 3.x"
    exit 1
fi

PLOT_SCRIPT="plot.py"
OUTPUT_DIR="comparisons"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Gerando comparações para todos circuitos"
echo "=========================================="
echo "Python: $PYTHON_CMD"
echo "Diretório de saída: $OUTPUT_DIR/"
echo ""

# Chua Circuit (Oscilador caótico)
echo "[1/7] Gerando: comparison_chua.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/chua.net --output "$OUTPUT_DIR/comparison_chua.png"

# DC Source com Diodo (Retificador)
echo "[2/7] Gerando: comparison_dc_source.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/dc_source.net --output "$OUTPUT_DIR/comparison_dc_source.png"

# LC Oscillator
echo "[3/7] Gerando: comparison_lc.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/lc.net --output "$OUTPUT_DIR/comparison_lc.png"

# OpAmp Rectifier (Retificador de precisão)
echo "[4/7] Gerando: comparison_opamp_rectifier.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/opamp_rectifier.net --output "$OUTPUT_DIR/comparison_opamp_rectifier.png"

# Oscilador com OpAmp e Diodos
echo "[5/7] Gerando: comparison_oscilator.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/oscilator.net --output "$OUTPUT_DIR/comparison_oscilator.png"

# Fonte PULSE
echo "[6/7] Gerando: comparison_pulse.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/pulse.net --output "$OUTPUT_DIR/comparison_pulse.png"

# Fonte Sinusoidal
echo "[7/7] Gerando: comparison_sinusoidal.png"
$PYTHON_CMD $PLOT_SCRIPT --net circuits/sinusoidal.net --output "$OUTPUT_DIR/comparison_sinusoidal.png"

echo ""
echo "=========================================="
echo "✅ Todas as comparações foram geradas!"
echo "=========================================="
echo ""
ls -lh "$OUTPUT_DIR"/comparison_*.png
