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
    parser.add_argument("--update", action="store_true", help="Força a atualização de issues existentes (Padrão: False para listas)")
    
    args = parser.parse_args()
    
    manager = IssueManager(dry_run=args.dry_run)
    all_data = []

    if args.source == "docx":
        # ... (files logic)
        files = glob.glob(os.path.join(args.path, "**/*.docx"), recursive=True) if os.path.isdir(args.path) else [args.path]
        files = [f for f in files if not os.path.basename(f).startswith('~$')]
            
        print(f"Encontrados {len(files)} arquivo(s) DOCX.")
        
        for f in files:
            print(f"Lendo: {os.path.basename(f)}")
            p = DocxParser(f)
            try:
                data = p.parse()
                # DOCX sempre atualiza por padrão pois é a fonte da verdade, a menos que (futuro) queiramos mudar
                # Mas para simplificar e atender o pedido, vamos assumir que DOCX sempre deve atualizar?
                # O usuário pediu parametro 'apenas para process-list'.
                # Então vou passar update_existing=True HARDCODED para docx, e args.update para list.
                manager.process_data(data, update_existing=True) 
            except Exception as e:
                print(f"❌ Erro ao processar arquivo {f}: {e}")

    elif args.source == "list":
        print(f"Lendo lista: {args.path}")
        p = TextListParser(args.path)
        try:
            data = p.parse()
            # LIST só atualiza se a flag --update for passada
            manager.process_data(data, update_existing=args.update)
        except Exception as e:
            print(f"❌ Erro ao processar lista: {e}")

if __name__ == "__main__":
    main()
