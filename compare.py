import matplotlib.pyplot as plt
import os

def ler_arquivo_sim(caminho):
    """Lê um arquivo .sim e retorna os dados."""
    try:
        with open(caminho, 'r') as f:
            linhas = f.readlines()
        
        # Encontrar o cabeçalho (primeira linha que não começa com *)
        cabecalho = None
        dados = []
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:  # Ignorar linhas vazias
                continue
            if linha.startswith('*'):  # Ignorar linhas de comentário
                continue
            
            if cabecalho is None:
                # Primeira linha válida é o cabeçalho
                cabecalho = linha.split()
            else:
                # Demais linhas são dados
                valores = [float(x) for x in linha.split()]
                dados.append(valores)
        
        return cabecalho, dados
    
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None, None

def escolher_arquivo():
    """Solicita o caminho do arquivo até que seja válido."""
    while True:
        caminho = input("Insira o caminho do arquivo: ").strip()
        cabecalho, dados = ler_arquivo_sim(caminho)
        
        if cabecalho is None:
            print("Arquivo não encontrado.")
        else:
            return caminho, cabecalho, dados

def escolher_colunas(cabecalho):
    """Exibe as variáveis disponíveis e solicita a escolha dos eixos."""
    print("\nLista de variáveis:")
    for i, var in enumerate(cabecalho):
        print(f"[{i}] {var}")
    
    while True:
        try:
            x = int(input("Escolha o eixo x: ").strip())
            if 0 <= x < len(cabecalho):
                break
            print(f"Escolha um índice entre 0 e {len(cabecalho)-1}")
        except ValueError:
            print("Por favor, insira um número válido.")
    
    while True:
        try:
            y = int(input("Escolha o eixo y: ").strip())
            if 0 <= y < len(cabecalho):
                break
            print(f"Escolha um índice entre 0 e {len(cabecalho)-1}")
        except ValueError:
            print("Por favor, insira um número válido.")
    
    return x, y

def extrair_dados(dados, idx_x, idx_y):
    """Extrai as colunas x e y dos dados."""
    x = [linha[idx_x] for linha in dados]
    y = [linha[idx_y] for linha in dados]
    return x, y

def main():
    print("=== Plotador de Arquivos .sim ===\n")
    
    # Primeiro arquivo
    print("--- PRIMEIRO ARQUIVO ---")
    caminho1, cabecalho1, dados1 = escolher_arquivo()
    idx_x1, idx_y1 = escolher_colunas(cabecalho1)
    x1, y1 = extrair_dados(dados1, idx_x1, idx_y1)
    nome_arquivo1 = os.path.basename(caminho1)
    
    # Segundo arquivo (opcional)
    print("\n--- SEGUNDO ARQUIVO (opcional) ---")
    resposta = input("Deseja plotar um segundo arquivo? (s/n): ").strip().lower()
    
    if resposta == 's':
        caminho2, cabecalho2, dados2 = escolher_arquivo()
        idx_x2, idx_y2 = escolher_colunas(cabecalho2)
        x2, y2 = extrair_dados(dados2, idx_x2, idx_y2)
        nome_arquivo2 = os.path.basename(caminho2)
    else:
        x2, y2 = None, None
        nome_arquivo2 = None
    
    # Plotagem
    plt.figure(figsize=(10, 6))
    
    # Plotar primeiro arquivo
    plt.plot(x1, y1, 'b-', linewidth=1.5, label=f"{nome_arquivo1}: {cabecalho1[idx_y1]} vs {cabecalho1[idx_x1]}")
    
    # Plotar segundo arquivo se existir
    if x2 is not None:
        plt.plot(x2, y2, 'r-', linewidth=1.5, label=f"{nome_arquivo2}: {cabecalho2[idx_y2]} vs {cabecalho2[idx_x2]}")
    
    plt.xlabel(cabecalho1[idx_x1])
    plt.ylabel("Valor")
    plt.title("Comparação de Simulações de Circuitos")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    print("\nGráfico gerado! Fechando a janela encerrará o programa.")
    plt.show()

if __name__ == "__main__":
    main()