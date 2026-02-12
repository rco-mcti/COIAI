import docx
import os
import glob
import re
import sys
import json
import subprocess
import time

# Configuration
PROJECT_NUMBER = 1 # 'rco-mcti/1' -> project number 1
OWNER = "rco-mcti"
REPO = "COIAI" # Assuming repo name from path, but better if implicit or env var. 
# For GH CLI, usually we run in the context of the repo.
GITHUB_PROJECT_ID = "rco-mcti/1"
ASSIGNEE = "rco-mcti"

class HuParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.doc = docx.Document(filepath)
        self.hu_id = self._extract_hu_id()
        self.data = {
            "revisions": [],
            "identification": {},
            "user_story": "",
            "title": "",
            "labels": []
        }

    def _extract_hu_id(self):
        match = re.search(r'HistoriaUsuario_(\d+)', self.filename)
        return match.group(1) if match else "XXX"

    def parse(self):
        self._parse_revisions()
        self._parse_identification()
        self._parse_title()
        self._parse_user_story()

    def _parse_revisions(self):
        if len(self.doc.tables) > 0:
            table = self.doc.tables[0]
            for row in table.rows[1:]:
                cells = [c.text.strip() for c in row.cells]
                if len(cells) >= 4:
                    self.data["revisions"].append({
                        "version": cells[0],
                        "date": cells[1],
                        "description": cells[2],
                        "author": cells[3]
                    })

    def _parse_identification(self):
        if len(self.doc.tables) > 1:
            table = self.doc.tables[1]
            for row in table.rows:
                if len(row.cells) >= 2:
                    key = row.cells[0].text.strip().lower()
                    value = row.cells[1].text.strip()
                    
                    if "gerente" in key: self.data["identification"]["gerente"] = value
                    elif "projeto" in key: self.data["identification"]["projeto"] = value
                    elif "requisitante" in key: self.data["identification"]["requisitante"] = value
                    
                    elif "tema" in key: 
                        self.data["identification"]["tema"] = value
                        self._extract_label(value)
                    elif "épico" in key: 
                        self.data["identification"]["epico"] = value
                        self._extract_label(value)
                    elif "feature" in key: 
                        self.data["identification"]["feature"] = value
                        self._extract_label(value)

    def _extract_label(self, text):
        matches = re.findall(r'\b([A-Z]{1,2}\d{2,3})\b', text)
        for code in matches:
            if code not in self.data["labels"]:
                self.data["labels"].append(code)

    def _parse_title(self):
        if len(self.doc.tables) > 2:
            try:
                self.data["title"] = self.doc.tables[2].rows[0].cells[1].text.strip()
            except:
                self.data["title"] = "Título não encontrado"

    def _parse_user_story(self):
        if len(self.doc.tables) > 3:
            table = self.doc.tables[3]
            capture_next = False
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if cells and "Descrição" in cells[0]:
                    capture_next = True
                    continue
                if capture_next and cells:
                    self.data["user_story"] = cells[0]
                    break

    def generate_body(self):
        # Generates ONLY the body for gh issue create, NOT the frontmatter
        rev_rows = ""
        last_rev = self.data["revisions"][-1] if self.data["revisions"] else {"version": "", "date": "", "description": "", "author": ""}

        md = f"""
## 📝 Histórico de Revisões
| Campo         | Descrição |
| :------------ | :-------- |
| **Versão**    | {last_rev['version']} |
| **Data**      | {last_rev['date']} |
| **Descrição** | {last_rev['description']} |
| **Autor**     | {last_rev['author']} |

## 🆔 Identificação
| Campo                   | Descrição |
| :---------------------- | :-------- |
| **Projeto**             | {self.data['identification'].get('projeto', '')} |
| **Requisitante**        | {self.data['identification'].get('requisitante', '')} |
| **Gerente de Projetos** | {self.data['identification'].get('gerente', '')} |
| **Tema**                | {self.data['identification'].get('tema', '')} |
| **Épico**               | {self.data['identification'].get('epico', '')} |
| **Feature**             | {self.data['identification'].get('feature', '')} |


## 📖 Descrição (User Story)
{self.data['user_story']}

## 🔗 Referências
- P:\\CGIA\\OSTENSIVO\\CGIT\\03_COIAI\\Lei do Bem\\GESTAO DE SISTEMAS\\ARTEFATOS\\{self.filename}
"""
        return md

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        return None

def issue_exists(title):
    # Check if issue exists by searching for the exact title
    # gh issue list --search "in:title [HU006]: ..." --json number --limit 1
    # We need to escape quote for shell
    safe_title = title.replace('"', '\\"')
    cmd = f'gh issue list --search "in:title \\"{safe_title}\\"" --json number --limit 1'
    output = run_command(cmd)
    if output:
        issues = json.loads(output)
        if issues:
            return issues[0]['number']
    return None

import argparse

def process_file(filepath, dry_run=False):
    try:
        print(f"--- Processando: {os.path.basename(filepath)} ---")
        hu_parser = HuParser(filepath)
        hu_parser.parse()
        
        title = f"[HU{hu_parser.hu_id}]: {hu_parser.data['title']}"
        
        body = hu_parser.generate_body()
        labels = ",".join(hu_parser.data['labels']) if hu_parser.data['labels'] else ""

        # Check existence only if not dry-run or if we want to simulate properly (requires GH CLI)
        existing_number = None
        if not dry_run:
            existing_number = issue_exists(title)
        
        if dry_run:
            print(f"🔍 [DRY-RUN] Título: {title}")
            print(f"🔍 [DRY-RUN] Labels: {labels}")
            print(f"🔍 [DRY-RUN] Assignee: {ASSIGNEE}")
            print(f"🔍 [DRY-RUN] Project: {GITHUB_PROJECT_ID}")
            # print(f"🔍 [DRY-RUN] Corpo da Issue:\n{body}") 
            # Commented out body print to reduce noise, unless debugging
            
            # Simulate update check if possible, or just print intent
            # For dry-run, we might not know if it exists unless we actually query (which is safe read-only)
            # Let's query even in dry-run to show what WOULD happen (Create vs Update)
            existing_number_dry = issue_exists(title)
            if existing_number_dry:
                    print(f"🔍 [DRY-RUN] Issue #{existing_number_dry} já existe. Seria ATUALIZADA.")
            else:
                    print(f"🔍 [DRY-RUN] Issue não existe. Seria CRIADA.")
            
            print("-" * 40)
            return

        if existing_number:
            print(f"🔄 Issue já existe: #{existing_number}. Atualizando...")
            update_cmd = [
                "gh", "issue", "edit", str(existing_number),
                "--title", title,
                "--body", body,
                "--add-project", GITHUB_PROJECT_ID 
                # Note: edit --add-project helps ensure it's in the project if it wasn't
            ]
            if labels:
                update_cmd.extend(["--add-label", labels])
            
            try:
                subprocess.run(update_cmd, check=True, capture_output=True, text=True)
                print(f"✅ Issue #{existing_number} atualizada com sucesso.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao atualizar issue #{existing_number}: {e.stderr}")
            
            return

        # Create Issue
        print(f"🚀 Criando issue: {title}")
        create_cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", body,
            "--assignee", ASSIGNEE,
            "--project", GITHUB_PROJECT_ID
        ]
        
        if labels:
            create_cmd.extend(["--label", labels])
            
        # We use subprocess.run with list args for safety with quotes/spaces in body
        result = subprocess.run(create_cmd, check=True, capture_output=True, text=True)
        new_issue_url = result.stdout.strip()
        print(f"✅ Issue criada: {new_issue_url}")
        
        print("ℹ️ Issue atribuída ao projeto. Verifique se caiu na coluna correta (Backlog).")
        
    except Exception as e:
        print(f"❌ Erro ao processar {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process HU DOCX files and create GitHub Issues.")
    parser.add_argument("--dry-run", action="store_true", help="Run without creating issues on GitHub, printing output instead.")
    args = parser.parse_args()

    files = glob.glob("temp/*.docx")
    if not files:
        print("Nenhum arquivo .docx encontrado em temp/")
        return

    print(f"Encontrados {len(files)} arquivos para processar.")

    for filepath in files:
        process_file(filepath, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
