import os
import csv
import json
import xml.etree.ElementTree as ET

# Librerías especializadas
try: import pandas as pd; PANDAS_DISPONIBLE = True
except ImportError: PANDAS_DISPONIBLE = False

try: import PyPDF2; PDF_DISPONIBLE = True
except ImportError: PDF_DISPONIBLE = False

try: import docx; DOCX_DISPONIBLE = True
except ImportError: DOCX_DISPONIBLE = False

# El motor de "artillería pesada"
try: import textract; TEXTRACT_DISPONIBLE = True
except ImportError: TEXTRACT_DISPONIBLE = False

def extraer_texto_bruto(ruta_archivo: str) -> str:
    """
    Extractor universal para TECY. Normaliza virtualmente cualquier formato
    de documento a texto plano para su procesamiento léxico.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
        
    ext = os.path.splitext(ruta_archivo)[1].lower()

    # 1. Manejadores especializados (Eficiencia)
    try:
        if ext == '.txt' or ext == '.md':
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

        elif ext == '.csv':
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                return " ".join([" ".join(fila) for fila in csv.reader(f)])

        elif ext == '.json':
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                def _rec(o):
                    if isinstance(o, dict): return " ".join(_rec(v) for v in o.values())
                    if isinstance(o, list): return " ".join(_rec(i) for i in o)
                    return str(o)
                return _rec(json.load(f))

        elif ext in ['.xml', '.html', '.xhtml']:
            try:
                tree = ET.parse(ruta_archivo)
                return " ".join(elem.text for elem in tree.iter() if elem.text)
            except:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

        elif ext == '.pdf':
            if not PDF_DISPONIBLE: raise ImportError("Instala PyPDF2")
            with open(ruta_archivo, 'rb') as f:
                lector = PyPDF2.PdfReader(f)
                return "\n".join([p.extract_text() for p in lector.pages if p.extract_text()])

        elif ext == '.xlsx':
            if not PANDAS_DISPONIBLE: raise ImportError("Instala pandas y openpyxl")
            return " ".join(pd.read_excel(ruta_archivo, dtype=str).fillna("").values.flatten())

        elif ext == '.docx':
            if not DOCX_DISPONIBLE: raise ImportError("Instala python-docx")
            return "\n".join([p.text for p in docx.Document(ruta_archivo).paragraphs])

        # 2. El motor de "artillería pesada" para todo lo demás
        elif TEXTRACT_DISPONIBLE:
            # textract procesa binarios complejos y retorna bytes
            return textract.process(ruta_archivo).decode('utf-8', errors='ignore')

        # 3. Fallback de emergencia
        else:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    except Exception as e:
        raise RuntimeError(f"Error procesando {ruta_archivo}: {e}")