import re
import unicodedata

def clave_ordenamiento_espanol(palabra: str):
    """
    Permite agrupar palabras con tildes (como 'árbol') bajo su letra base 
    en el orden correcto, sin machacar ni destruir los caracteres originales.
    """
    forma_nfd = unicodedata.normalize('NFD', palabra)
    palabra_plana = "".join(c for c in forma_nfd if unicodedata.category(c) != 'Mn')
    return (palabra_plana, palabra)

def limpiar_y_ordenar_lexico(texto_crudo: str) -> list:
    """
    Limpia URLs, números y símbolos. Mantiene palabras del castellano 
    conservando acentos, diéresis y eñes. Elimina duplicados.
    """
    texto = unicodedata.normalize('NFC', texto_crudo)
    texto = re.sub(r'\bhttps?://\S+|\bwww\.\S+', ' ', texto)
    texto = re.sub(r'[0-9]', ' ', texto)
    texto = re.sub(r'[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]', ' ', texto)
    
    texto_minuscula = texto.lower()
    palabras_unicas = set(texto_minuscula.split())
    
    return sorted(palabras_unicas, key=clave_ordenamiento_espanol)
