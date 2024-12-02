import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

import google.generativeai as genai

def convert_pdf_to_text(folder_path):
    try:
        # Obtener una lista de archivos PDF en la carpeta
        pdf_files = [file for file in os.listdir(folder_path) if file.endswith('.pdf')]

        # Validar si no se encontraron archivos PDF
        if not pdf_files:
            print("No se encontraron archivos PDF en la carpeta proporcionada.")
            return None

        # Leer cada archivo PDF y extraer su texto
        text_list = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                text_list.append(text)
            except Exception as e:
                print(f"Error al procesar el archivo {pdf_file}: {e}")

        return text_list

    except Exception as e:
        print(f"Error al acceder a la carpeta: {e}")
        return None

def split_text_into_chunks(texts, chunk_size=500, chunk_overlap=50):
    """
    Divide cada texto en la lista de textos en chunks de tamaño determinado.
    
    Args:
        texts (list of str): Lista de textos a dividir en chunks.
        chunk_size (int): Tamaño máximo de cada chunk (por defecto 500 caracteres).
        chunk_overlap (int): Cantidad de solapamiento entre chunks (por defecto 50 caracteres).
    
    Returns:
        list of str: Lista de chunks de texto.
    """
    # Inicializar el TextSplitter de LangChain
    text_splitter = CharacterTextSplitter(
        separator="\n",  # Separar por saltos de línea, ajustable según necesidad
        chunk_size=chunk_size,  # Tamaño máximo de cada chunk
        chunk_overlap=chunk_overlap  # Cantidad de solapamiento entre los chunks
    )

    all_chunks = []
    for text in texts:
        # Dividir el texto en chunks
        chunks = text_splitter.split_text(text)
        all_chunks.extend(chunks)
    
    return all_chunks


def load_texts_from_folder(folder_path):
    """
    Carga todos los archivos de texto desde una carpeta y devuelve su contenido en una lista.
    """
    texts = []
    filenames = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                texts.append(file.read())
                filenames.append(filename)
    return texts, filenames

def create_persistent_client():
    """
    Crea un cliente persistente de Chroma.
    """
    client = chromadb.PersistentClient(
        path="test",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    return client


def add_texts_to_collection(collection, texts):
    """
    Añade los textos y nombres de archivo a una colección Chroma.
    """
    documents = texts
    ids = [f'id_{i}' for i,_ in enumerate(texts)]
    collection.add(documents=documents,ids=ids)



# MAIN LOOP
if __name__ == '__main__':

    cwd = os.getcwd()
    # Carpeta que contiene los documentos
    folder = 'pdfs'  
    folder_path=os.path.join(cwd,folder)
    print('Cargando textos desde la carpeta...')
    textos = convert_pdf_to_text(folder_path)
    print(f'Se cargaron {len(textos)} documentos.')

    print('Dividiendo en chunks...')
    chunks = split_text_into_chunks(textos, chunk_size=1000, chunk_overlap=300)
    print('Chunks  divididos')
    
    print('Creando cliente de Chroma persistente...')
    chroma_client = create_persistent_client()
    print('Cliente creado.')

    print('Creando colección en la base de datos...')
    chroma_collection = chroma_client.create_collection(name='planes-de-estudio-carreras-unam')
    print('Colección inicializada.')

    print('Añadiendo chunks a la colección...')
    add_texts_to_collection(chroma_collection, chunks)
    print('Datos añadidos exitosamente.')

    print('Programa terminado.')
