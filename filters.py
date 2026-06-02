import os
import unicodedata

def obtener_letra_base(palabra: str) -> str:
    """
    Resuelve la inicial real sin tilde de un token léxico.
    á -> a, ñ -> ñ.
    """
    if not palabra:
        return ""
    primera_letra = palabra[0].lower()
    if primera_letra == 'ñ':
        return 'ñ'
    forma_nfd = unicodedata.normalize('NFD', primera_letra)
    return "".join(c for c in forma_nfd if unicodedata.category(c) != 'Mn')

def filtrar_por_letras(ruta_clean_tmp: str, letras_objetivo: set) -> list:
    """
    Lee de forma eficiente el archivo de auditoría .clean.tmp extrae 
    exclusivamente los tokens que se correspondan con el set de iniciales.
    """
    palabras_filtradas = []
    if not os.path.exists(ruta_clean_tmp):
        return []
        
    with open(ruta_clean_tmp, 'r', encoding='utf-8') as f:
        for linea in f:
            palabra = linea.strip()
            if palabra and obtener_letra_base(palabra) in letras_objetivo:
                palabras_filtradas.append(palabra)
                
    return palabras_filtradas