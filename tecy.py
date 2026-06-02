import os
import sys
import unicodedata

DIR_TECY_INTERNO = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIR_TECY_INTERNO)

DIR_TMP = os.path.join(DIR_TECY_INTERNO, "tmp")
DIR_LETTERS = os.path.join(BASE_DIR, "letters")
DIR_ALLS = os.path.join(BASE_DIR, "alls")

os.makedirs(DIR_TMP, exist_ok=True)
os.makedirs(DIR_LETTERS, exist_ok=True)
os.makedirs(DIR_ALLS, exist_ok=True)

if DIR_TECY_INTERNO not in sys.path:
    sys.path.insert(0, DIR_TECY_INTERNO)

from extractor import extraer_texto_bruto
from cleaner import limpiar_y_ordenar_lexico
from filters import filtrar_por_letras
from exporter import guardar_diccionario_letras

def español_sort_key(palabra):
    """
    Genera una clave de ordenamiento que respeta las reglas del idioma español:
    1. Trata las vocales con acento o diéresis (á, é, í, ó, ú, ü) como vocales normales.
    2. Posiciona la 'ñ' estrictamente después de la 'n' y antes de la 'o'.
    """
    palabra_lower = palabra.lower()
    
    resultado = []
    for char in palabra_lower:
        if char == 'ñ':
            resultado.append('n~')
        else:
            char_normalizado = unicodedata.normalize('NFD', char)
            char_base = [c for c in char_normalizado if unicodedata.category(c) != 'Mn']
            if char_base:
                resultado.append(char_base[0])
            else:
                resultado.append(char)
                
    return "".join(resultado)

def ordenar_lista_español(lista_palabras):
    """Ordena una lista o set de palabras bajo el estándar estricto del español."""
    return sorted(list(lista_palabras), key=español_sort_key)

def mostrar_ayuda():
    print("TECY - Extractor Léxico Documental (Base Estable v1.5 - Oculto)")
    print("\n[MÁQUINA DE FILTRADO E INYECCIÓN CON ORDEN ALFABÉTICO ESPAÑOL (Ñ / ACENTOS INTEGRADOS)]")
    print("\n1. Modos de Salida Estándar (Automáticos del sistema):")
    print("  tecy all <archivo_entrada>         -> Exporta todo el léxico a alls/all_<archivo>.txt")
    print("  tecy [-flags...] <archivo_entrada>   -> Exporta filtros por inicial a letters/<flags>_<archivo>.txt")
    print("\n2. Modos de Inyección (Fusión incremental en Base de Datos Personalizada):")
    print("  tecy all test.txt database.txt     -> Fusiona TODO el léxico ordenado en database.txt")
    print("  tecy -a -b test.txt database.txt   -> Filtra letras 'a' y 'b' y las inyecta en database.txt")

def inyectar_en_base_de_datos(nuevas_palabras, ruta_salida):
    """
    Toma un set de palabras procesadas y las fusiona de forma incremental e inteligente
    con un archivo objetivo de texto plano, formateándolo y ordenándolo alfabéticamente.
    """
    palabras_totales = set(nuevas_palabras)
    
    if os.path.exists(ruta_salida):
        try:
            with open(ruta_salida, 'r', encoding='utf-8') as f:
                for linea in f:
                    palabra = linea.strip()
                    if palabra:
                        palabras_totales.add(palabra)
            print(f"[Inyect] Leyendo léxico existente en: {os.path.basename(ruta_salida)}")
        except Exception as e:
            print(f"[Advertencia] No se pudo leer el archivo destino: {e}")

    lista_final_ordenada = ordenar_lista_español(palabras_totales)

    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            for palabra in lista_final_ordenada:
                f.write(f"{palabra}\n")
        print(f"[Éxito Inyección] Archivo formateado y actualizado: {ruta_salida} ({len(lista_final_ordenada)} palabras totales)")
    except Exception as e:
        print(f"Error crítico escribiendo en el archivo de inyección: {e}", file=sys.stderr)

def main():
    args = sys.argv[1:]
    
    if not args or "-h" in args or "--help" in args:
        mostrar_ayuda()
        sys.exit(0)

    lista_flags = []
    argumentos_posicionales = []
    ejecutar_modo_all = False

    LETRAS_VALIDAS = set("abcdefghijklmnñopqrstuvwxyz")

    for arg in args:
        if arg.lower() == "all":
            ejecutar_modo_all = True
        elif arg.startswith("-"):
            letras_filtradas = []
            for char in arg[1:].lower():
                if char in LETRAS_VALIDAS:
                    letras_filtradas.append(char)
            flag_limpio = "".join(sorted(list(set(letras_filtradas))))
            if flag_limpio:
                lista_flags.append(flag_limpio)
        else:
            argumentos_posicionales.append(arg)

    ruta_documento = None
    ruta_salida_personalizada = None

    if len(argumentos_posicionales) == 1:
        ruta_documento = argumentos_posicionales[0]
    elif len(argumentos_posicionales) >= 2:
        ruta_documento = argumentos_posicionales[0]
        ruta_salida_personalizada = argumentos_posicionales[1]

    if not ruta_documento:
        print("Error: No se especificó el archivo de entrada.", file=sys.stderr)
        sys.exit(1)

    try:
        texto_crudo = extraer_texto_bruto(ruta_documento)
        
        lexico_completo = limpiar_y_ordenar_lexico(texto_crudo)
        
        nombre_base = os.path.splitext(os.path.basename(ruta_documento))[0]
        ruta_tmp_final = os.path.join(DIR_TMP, f"{nombre_base}.clean.tmp")
        
        lexico_completo_ordenado = ordenar_lista_español(lexico_completo)
        with open(ruta_tmp_final, 'w', encoding='utf-8') as f:
            for palabra in lexico_completo_ordenado:
                f.write(f"{palabra}\n")
                
        print(f"[Auditoría OK] .tecy/tmp/{nombre_base}.clean.tmp ({len(lexico_completo_ordenado)} palabras únicas)")
        
        if ejecutar_modo_all:
            if ruta_salida_personalizada:
                inyectar_en_base_de_datos(lexico_completo_ordenado, ruta_salida_personalizada)
            else:
                guardar_diccionario_letras(lexico_completo_ordenado, "all", ruta_documento, DIR_ALLS)

        if lista_flags:
            letras_totales_a_filtrar = set()
            for flag in lista_flags:
                letras_totales_a_filtrar.update(list(flag))
            
            palabras_filtradas = filtrar_por_letras(ruta_tmp_final, letras_totales_a_filtrar)
            palabras_filtradas_ordenadas = ordenar_lista_español(palabras_filtradas)
            
            if ruta_salida_personalizada:
                inyectar_en_base_de_datos(palabras_filtradas_ordenadas, ruta_salida_personalizada)
            else:
                flag_representativo = "".join(sorted(list(letras_totales_a_filtrar)))
                guardar_diccionario_letras(palabras_filtradas_ordenadas, flag_representativo, ruta_documento, DIR_LETTERS)
            
    except Exception as e:
        print(f"Error crítico en el pipeline: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()