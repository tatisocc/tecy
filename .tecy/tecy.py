import sys
import os
import argparse
import re
import unicodedata
import json 
import xml.etree.ElementTree as ET 

try:
    import pandas as pd
    PANDAS_DISPONIBLE = True
except ImportError:
    PANDAS_DISPONIBLE = False

try:
    import PyPDF2
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

CARPETA_SALIDA_BASE = os.path.expanduser("~/.tecy")
SEPARADOR = ":"

def limpiar_y_separar_linea(linea):

    linea = unicodedata.normalize('NFC', linea.strip())
    
    linea = re.sub(r'\bhttps?://\S+|\bwww\.\S+', ' ', linea)

    linea = re.sub(r'[0-9]', ' ', linea)

    linea = re.sub(r'[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]', ' ', linea)
    
    palabras = ' '.join(linea.split()).split(' ')
    
    elementos_limpios = [p for p in palabras if p]
            
    if not elementos_limpios:
        return None 
        
    return SEPARADOR.join(elementos_limpios)

def convertir_a_texto_simple(lineas):

    resultado = []
    
    for linea in lineas:
        linea_convertida = limpiar_y_separar_linea(linea)
        if linea_convertida:
            resultado.append(linea_convertida)
        
    return "\n".join(resultado)


def extraer_texto_pdf(ruta_entrada):
    if not PDF_DISPONIBLE:
        print("ADVERTENCIA: PyPDF2 no está instalado. No se puede procesar PDF.")
        return None
        
    try:
        texto_total = []
        with open(ruta_entrada, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texto_total.append(page.extract_text())
        
        return "\n".join(texto_total)
    
    except Exception as e:
        print(f"INFO: Falló la lectura como PDF: {e}")
        return None

def extraer_texto_xlsx(ruta_entrada):
    if not PANDAS_DISPONIBLE:
        print("ADVERTENCIA: Pandas y Openpyxl no están instalados. No se puede procesar XLSX.")
        return None
        
    try:
        xls = pd.ExcelFile(ruta_entrada)
        texto_total = []
        
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            texto_total.append(df.to_string(header=True, index=False))
            
        return "\n".join(texto_total)
    
    except Exception as e:
        print(f"INFO: Falló la lectura como XLSX: {e}")
        return None

def extraer_texto_json(ruta_entrada):
    try:
        with open(ruta_entrada, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texto_total = []
        
        def traverse(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)
            elif isinstance(obj, str):
                texto_total.append(obj)

        traverse(data)
        return "\n".join(texto_total)
    
    except Exception as e:
        return None

def extraer_texto_xml(ruta_entrada):
    try:
        tree = ET.parse(ruta_entrada)
        root = tree.getroot()
        texto_total = []
        
        for element in root.iter():
            if element.text and element.text.strip():
                texto_total.append(element.text.strip())
            for value in element.attrib.values():
                texto_total.append(value)
                
        return "\n".join(texto_total)
    
    except Exception as e:
        return None


def procesar_archivo(ruta_entrada):

    if not os.path.exists(ruta_entrada):
        print(f"ERROR: Archivo no encontrado en la ruta: {ruta_entrada}")
        return

    nombre_archivo = os.path.basename(ruta_entrada)
    extension = os.path.splitext(nombre_archivo)[1].lower()
    
    texto_bruto = None
    
    if extension == '.pdf':
        print("INFO: Intentando leer como PDF...")
        texto_bruto = extraer_texto_pdf(ruta_entrada)

    if texto_bruto is None and extension in ['.xlsx']:
        print("INFO: Intentando leer como XLSX...")
        texto_bruto = extraer_texto_xlsx(ruta_entrada)

    if texto_bruto is None and extension in ['.json']:
        print("INFO: Intentando leer como JSON...")
        texto_bruto = extraer_texto_json(ruta_entrada)

    if texto_bruto is None and extension in ['.xml', '.html', '.htm']:
        print("INFO: Intentando leer como XML/HTML...")
        texto_bruto = extraer_texto_xml(ruta_entrada)

    if texto_bruto is None:
        print("INFO: Leyendo como texto plano (CSV, TXT, o fallback)...")
        codificaciones = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in codificaciones:
            try:
                with open(ruta_entrada, 'r', encoding=encoding) as f:
                    texto_bruto = f.read()
                print(f"INFO: Archivo leído exitosamente como texto ({extension}) con codificación '{encoding}'.")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"ERROR al leer el archivo {ruta_entrada}: {e}")
                return
                
        if texto_bruto is None:
            print("ERROR: No se pudo leer el archivo con las codificaciones intentadas (UTF-8, Latin-1, CP1252).")
            return

    lineas_input = texto_bruto.splitlines()

    texto_convertido = convertir_a_texto_simple(lineas_input)
    
    os.makedirs(CARPETA_SALIDA_BASE, exist_ok=True)
    
    nombre_base, _ = os.path.splitext(nombre_archivo)
    ruta_salida = os.path.join(CARPETA_SALIDA_BASE, f"{nombre_base}.txt")
    
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(texto_convertido)
        
        print(f"Éxito: Archivo limpio guardado en {ruta_salida}")
        
    except Exception as e:
        print(f"ERROR al escribir el archivo de salida {ruta_salida}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Tecy: Convierte archivos en texto limpio sin números ni enlaces. Soporta TXT, CSV, JSON, XML/HTML, XLSX, y PDF.",
        epilog=f"La salida limpia se guarda en: {CARPETA_SALIDA_BASE}",
        add_help=False
    )
    try:
        parser.add_argument("archivo_entrada", type=str) 
        args = parser.parse_args()
    except SystemExit:
        if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
            print(parser.description)
            print(f"\nUso: python3 {os.path.basename(sys.argv[0])} <archivo_entrada>")
            print(f"Salida: {CARPETA_SALIDA_BASE}/<nombre_archivo>.txt")
            print("\nNOTA: Para XLSX y PDF, debe instalar las librerías 'pandas' y 'PyPDF2'.")
        return
    
    if args.archivo_entrada in ('-h', '--help'):
        print(parser.description)
        print(f"\nUso: python3 {os.path.basename(sys.argv[0])} <archivo_entrada>")
        print(f"Salida: {CARPETA_SALIDA_BASE}/<nombre_archivo>.txt")
        print("\nNOTA: Para XLSX y PDF, debe instalar las librerías 'pandas' y 'PyPDF2'.")
        return


    procesar_archivo(args.archivo_entrada)

if __name__ == "__main__":
    main()
