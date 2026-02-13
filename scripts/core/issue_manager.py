import os
from jinja2 import Environment, FileSystemLoader
from .github_client import GithubClient

class IssueManager:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.client = GithubClient()
        
        # Configurar Jinja2
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template('issue_template.md.j2')

    def process_data(self, data_list):
        if not data_list:
            print("Nenhum dado para processar.")
            return

        print(f"--- Processando {len(data_list)} item(s) ---")

        for item in data_list:
            hu_id = item.get('id', 'XXX')
            title_text = item.get('title', 'Sem Título')
            full_title = f"[{hu_id}]: {title_text}"

            # Renderiza o corpo usando o template Jinja2
            # O template trata campos vazios usando | default('-')
            body = self.template.render(**item)

            if self.dry_run:
                print(f"🔍 [DRY-RUN] Título: {full_title}")
                # print(f"🔍 [DRY-RUN] Corpo:\n{body[:100]}...") # Preview
                existing_number = self.client.issue_exists(f"[{hu_id}]")
                if existing_number:
                    print(f"🔍 [DRY-RUN] Issue #{existing_number} já existe. Seria ATUALIZADA.")
                else:
                    print(f"🔍 [DRY-RUN] Issue não existe. Seria CRIADA.")
                print("-" * 30)
                continue

            # Verifica existência pelo ID no título (ex: [HU076])
            existing_number = self.client.issue_exists(f"[{hu_id}]")

            if existing_number:
                print(f"🔄 Issue já existe: #{existing_number}. Atualizando...")
                self.client.update_issue(existing_number, full_title, body)
                print(f"✅ Issue #{existing_number} atualizada.")
                self.client.add_to_project(existing_number, 1, "rco-mcti", "COIAI")
            else:
                print(f"🚀 Criando issue: {full_title}")
                result_url = self.client.create_issue(full_title, body)
                print(f"✅ Issue criada: {result_url}")
                
                # Extrair número da URL
                if result_url:
                    try:
                        new_number = result_url.split('/')[-1]
                        self.client.add_to_project(new_number, 1, "rco-mcti", "COIAI")
                    except:
                        print("⚠️ Não foi possível extrair número da issue para adicionar ao projeto.")
