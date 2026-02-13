import re
import os
import sys

class HuListParser:
    """
    Classe para analisar arquivos Markdown e extrair Histórias de Usuário (HUs).
    Espera linhas no formato: HU<numero> - <descricao>
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.hus = []
        self.sprint = None

    def parse(self):
        """Lê o arquivo e extrai as HUs baseadas em regex."""
        if not os.path.exists(self.filepath):
            print(f"Erro: Arquivo não encontrado: {self.filepath}")
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Regex para capturar HU<id> - <descricao>
            pattern_hu = re.compile(r'^HU\s*(\d+)\s*[-–]\s*(.*)', re.IGNORECASE)
            # Regex para capturar Sprint (ex: "Sprint 6", "(Sprint 6)")
            pattern_sprint = re.compile(r'Sprint\s+(\d+)', re.IGNORECASE)

            for line in lines:
                line = line.strip()
                
                # Check for Sprint if not found yet
                if not self.sprint:
                    match_sprint = pattern_sprint.search(line)
                    if match_sprint:
                        self.sprint = match_sprint.group(1)

                match_hu = pattern_hu.match(line)
                if match_hu:
                    hu_number = int(match_hu.group(1)) # Pega o número
                    hu_id = f"HU{hu_number:03d}"   # Formata com 3 dígitos (ex: HU076)
                    description = match_hu.group(2).strip()
                    self.hus.append({'id': hu_id, 'description': description})
            
            return self.hus

        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return []

    def print_hus(self):
        """Imprime as HUs encontradas no console."""
        sprint_info = f" (Sprint {self.sprint})" if self.sprint else ""
        print(f"--- HUs encontradas em '{self.filepath}'{sprint_info} ---")
        
        if not self.hus:
            print("Nenhuma HU encontrada.")
            return

        for hu in self.hus:
            print(f"[{hu['id']}] {hu['description']}")
        print(f"-------------------------------------------")
        print(f"Total: {len(self.hus)}")

if __name__ == "__main__":
    # Caminho padrão ou argumento
    target_file = "novas_HUs.md"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    parser = HuListParser(target_file)
    parser.parse()
    parser.print_hus()
