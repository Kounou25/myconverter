
import os

def SizeCalc(fichier):
   
        file_size = fichier.size

        # Convertir la taille en kilo-octets (Ko) ou mégaoctets (Mo) si nécessaire
        if file_size < 1024:
            file_size_formatted = f"{file_size} octets"
        elif file_size < 1024 * 1024:
            file_size_formatted = f"{file_size / 1024:.2f} Ko"
        else:
            file_size_formatted = f"{file_size / (1024 * 1024):.2f} Mo"

        return file_size_formatted