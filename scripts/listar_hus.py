import re
import os
import sys
import argparse
import subprocess
import json

class HuListParser:
    """
    Classe para analisar arquivos Markdown e extrair Histórias de Usuário (HUs).
    Espera linhas no formato: HU<numero> - <descricao>
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.hus = []
        # self.sprint removido, tratado localmente no loop

    def parse(self):
        """Lê o arquivo e extrai as HUs baseadas em regex, detectando a Sprint atual."""
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

            current_sprint = "?"

            for line in lines:
                line = line.strip()
                
                # Check for Sprint header
                match_sprint = pattern_sprint.search(line)
                if match_sprint:
                    current_sprint = match_sprint.group(1)
                    continue

                match_hu = pattern_hu.match(line)
                if match_hu:
                    hu_number = int(match_hu.group(1)) # Pega o número
                    hu_id = f"HU{hu_number:03d}"   # Formata com 3 dígitos (ex: HU076)
                    description = match_hu.group(2).strip()
                    self.hus.append({
                        'sprint': current_sprint,
                        'id': hu_id, 
                        'description': description
                    })
            
            return self.hus

        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return []

    def check_issue_exists(self, title_pattern):
        """Verifica se uma issue com o título já existe."""
        try:
            # Busca issues com o título especificado
            cmd = ['gh', 'issue', 'list', '--search', f'"{title_pattern}"', '--json', 'title,number', '--state', 'all']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            issues = json.loads(result.stdout)
            return len(issues) > 0
        except Exception as e:
            print(f"⚠️  Erro ao verificar existência da issue: {e}")
            return False

    def create_github_issues(self):
        """Cria as issues no GitHub se não existirem."""
        if not self.hus:
            print("Nenhuma HU encontrada para processar.")
            return

        print(f"--- Iniciando criação de {len(self.hus)} Issues ---")
        
        for hu in self.hus:
            sprint_val = hu['sprint']
            hu_id = hu['id'] # Ex: HU076
            description = hu['description']
            
            # Formato do Título simplificado para checagem e criação
            # "[HU076]: Descrição..."
            title = f"[{hu_id}]: {description}"
            
            # Verifica se já existe (busca pelo ID da HU no título para evitar duplicatas mesmo se a descrição mudar levemente)
            if self.check_issue_exists(f"[{hu_id}]"):
                print(f"⏭️  Issue já existe (ID encontrado): {hu_id}")
                continue
                
            print(f"🚀 Criando issue: {title}")
            
            # Labels removed by user request
            # labels = ["HU"]
            # if sprint_val != "?":
            #     labels.append(f"Sprint {sprint_val}")
            # labels_str = ",".join(labels)
            
            # Corpo simples
            body = (
                f"**História de Usuário**: {hu_id}\n"
                f"**Sprint**: {sprint_val}\n"
                f"**Descrição**: {description}\n\n"
                f"--- \n*Criado automaticamente via workflow create-issues.*"
            )
            
            try:
                cmd = [
                    'gh', 'issue', 'create',
                    '--title', title,
                    '--body', body
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
                print(f"✅ Criada com sucesso: {result.stdout.strip()}")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Falha ao criar issue '{title}': {e.stderr}")

    def print_hus(self):
        """Imprime as HUs encontradas no console formatadas como CSV."""
        if not self.hus:
            print("Nenhuma HU encontrada.")
            return

        # Header solicitado
        print("Sprint ; HU ; Título")
        
        for hu in self.hus:
            print(f"{hu['sprint']} ; {hu['id']} ; {hu['description']}")
        
        print(f"-------------------------------------------")
        print(f"Total: {len(self.hus)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Listar ou Criar HUs a partir de arquivo de texto.")
    parser.add_argument("file", nargs="?", default="lista_HU.txt", help="Arquivo de entrada")
    parser.add_argument("--create", action="store_true", help="Criar issues no GitHub")
    
    args = parser.parse_args()
    
    hu_parser = HuListParser(args.file)
    hu_parser.parse()
    
    if args.create:
        hu_parser.create_github_issues()
    else:
        hu_parser.print_hus()
