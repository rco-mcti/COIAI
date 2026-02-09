import sys
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python pdf_to_issue.py <caminho_do_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    filename = os.path.basename(pdf_path)
    content = extract_text_from_pdf(pdf_path)

    if not content:
        sys.exit(1)

    # Cria um corpo básico para a Issue usando o conteúdo extraído
    # No futuro, aqui entraria a lógica de IA para organizar nos campos do template
    issue_title = f"[AUTO-HU]: {filename.replace('.pdf', '')}"
    issue_body = f"""
## 📄 Conteúdo Extraído do PDF ({filename})

{content}

---
> [!NOTE]
> Esta issue foi gerada automaticamente. Use o template de HU para organizar as informações acima.
"""

    # Print para o GitHub Action capturar
    print(f"TITLE={issue_title}")
    # Usando delimitadores para o corpo (multiline strings no GH Actions)
    print("BODY<<EOF")
    print(issue_body)
    print("EOF")

if __name__ == "__main__":
    main()
