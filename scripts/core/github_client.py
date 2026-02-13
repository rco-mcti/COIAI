import subprocess
import json
import logging

class GithubClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run_command(self, command):
        """Executa um comando shell e retorna a saída (stdout)."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {command}")
            self.logger.error(f"Stderr: {e.stderr}")
            raise e

    def issue_exists(self, title_pattern):
        """
        Verifica se uma issue existe buscando pelo título.
        Retorna o número da issue se encontrar, ou None.
        """
        # Escapa aspas para o shell
        safe_title = title_pattern.replace('"', '\\"')
        cmd = ['gh', 'issue', 'list', '--search', f'"{safe_title}"', '--json', 'number', '--limit', '1', '--state', 'all']
        
        try:
            output = self.run_command(cmd)
            issues = json.loads(output)
            if issues:
                return issues[0]['number']
            return None
        except Exception as e:
            self.logger.warning(f"Failed to check issue existence: {e}")
            return None

    def create_issue(self, title, body):
        """Cria uma nova issue."""
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body
        ]
        return self.run_command(cmd)

    def update_issue(self, number, title, body):
        """Atualiza uma issue existente."""
        cmd = [
            'gh', 'issue', 'edit', str(number),
            '--title', title,
            '--body', body
        ]
        return self.run_command(cmd)

    def add_to_project(self, issue_number, project_number, owner, repo):
        """Adiciona a issue a um projeto (V2)."""
        # gh project item-add <project-number> --owner <owner> --url <issue-url>
        issue_url = f"https://github.com/{owner}/{repo}/issues/{issue_number}"
        cmd = [
            'gh', 'project', 'item-add', str(project_number),
            '--owner', owner,
            '--url', issue_url
        ]
        try:
            self.run_command(cmd)
            return True
        except Exception as e:
            self.logger.warning(f"Failed to add to project: {e}")
            return False
