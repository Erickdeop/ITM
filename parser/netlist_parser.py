###### Responsável por ler e interpretar o arquivo de netlist ######
from components.componentes import Componentes
from core.nodemap import NodeMap

class NetlistParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self):
        with open(self.filepath, "r") as f:
            linhas = [ln.strip() for ln in f if ln.strip()]
        
        if not linhas:
            raise ValueError("Arquivo vazio.")
        
        n_decl = int(linhas[0].split()[0])
        nodemap = NodeMap()
        comp = Componentes()
        elementos = []

        for linha in linhas[1:]:
            elem = comp.parse_linha(linha, nodemap)
            if elem:
                elementos.append(elem)

        return elementos, nodemap
