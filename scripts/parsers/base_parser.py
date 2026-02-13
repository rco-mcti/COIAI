from abc import ABC, abstractmethod

class BaseParser(ABC):
    def __init__(self, filepath):
        self.filepath = filepath

    @abstractmethod
    def parse(self):
        """
        Método abstrato que deve retornar uma lista de dicionários com os dados das HUs.
        Exemplo de retorno:
        [
            {
                "id": "HU001",
                "title": "Titulo",
                "user_story": "Como usuario...",
                "revisions": [...],
                "identification": {...},
                "references": "..."
            }
        ]
        """
        pass
