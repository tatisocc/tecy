import os

def guardar_diccionario_letras(palabras: list, letras_grupo: str, nombre_original: str, dir_letters: str):
    """
    Graba el archivo físico correspondiente en el almacén de salida /letters.
    """
    if not palabras:
        print(f"[Aviso] No se encontraron palabras para el filtro -{letras_grupo}")
        return
        
    nombre_puro = os.path.splitext(os.path.basename(nombre_original))[0]
    nombre_salida = f"{letras_grupo.lower()}_{nombre_puro}.txt"
    ruta_salida = os.path.join(dir_letters, nombre_salida)
    
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        for palabra in palabras:
            f.write(f"{palabra}\n")
            
    print(f"[Exportado] letters/{nombre_salida} ({len(palabras)} palabras)")
