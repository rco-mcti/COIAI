import re
import os
from datetime import datetime
from .base_parser import BaseParser

class TextListParser(BaseParser):
    def parse(self):
        if not os.path.exists(self.filepath):
            return []

        hus = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Regex para capturar HU<id> - <descricao>
        pattern_hu = re.compile(r'^HU\s*(\d+)\s*[-–]\s*(.*)', re.IGNORECASE)
        # Regex para capturar Sprint
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
                hu_id_num = int(match_hu.group(1))
                hu_id = f"HU{hu_id_num:03d}"
                description = match_hu.group(2).strip()

                # Monta dicionário compatível com o template
                hu_data = {
                    "id": hu_id,
                    "title": description, # Na lista simples, o título é a descrição curta
                    "user_story": f"**História de Usuário**: {hu_id}<br>**Sprint**: {current_sprint}<br>**Descrição**: {description}",
                    "sprint": current_sprint, # Extra field, might be useful
                    "revisions": [], # Lista vazia, template tratará com '-'
                    "identification": {}, # Dict vazio, template tratará com '-'
                    "references": "", # Vazio
                    "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                hus.append(hu_data)
        
        return hus
