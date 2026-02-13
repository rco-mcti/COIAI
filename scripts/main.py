import argparse
import os
import glob
from core.issue_manager import IssueManager
from parsers.docx_parser import DocxParser
from parsers.text_list_parser import TextListParser

def main():
    parser = argparse.ArgumentParser(description="Orquestrador de Issues do GitHub (COIAI)")
    parser.add_argument("--source", choices=["docx", "list"], required=True, help="Tipo de fonte de dados")
    parser.add_argument("--path", required=True, help="Caminho do arquivo ou diretório base")
    parser.add_argument("--dry-run", action="store_true", help="Simula execução sem alterações no GitHub")
    
    args = parser.parse_args()
    
    manager = IssueManager(dry_run=args.dry_run)
    all_data = []

    if args.source == "docx":
        # Busca recursiva de .docx se for diretório, ou arquivo único
        if os.path.isdir(args.path):
            files = glob.glob(os.path.join(args.path, "**/*.docx"), recursive=True)
            files = [f for f in files if not os.path.basename(f).startswith('~$')] # Ignora temp files do Word
        else:
            files = [args.path]
            
        print(f"Encontrados {len(files)} arquivo(s) DOCX.")
        
        for f in files:
            print(f"Lendo: {os.path.basename(f)}")
            p = DocxParser(f)
            # Acumula ou processa um a um? 
            # O process_hu.py processava um a um. Vamos manter.
            try:
                data = p.parse()
                manager.process_data(data)
            except Exception as e:
                print(f"❌ Erro ao processar arquivo {f}: {e}")

    elif args.source == "list":
        print(f"Lendo lista: {args.path}")
        p = TextListParser(args.path)
        try:
            data = p.parse()
            manager.process_data(data)
        except Exception as e:
            print(f"❌ Erro ao processar lista: {e}")

if __name__ == "__main__":
    main()
