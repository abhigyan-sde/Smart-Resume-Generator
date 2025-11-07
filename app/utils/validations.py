

class Validation:

    @staticmethod
    def validateFileExtension(fileName : str) -> bool:
         if not fileName.lower().endswith((".pdf", ".doc", ".docx")):
            return False
         return True
         