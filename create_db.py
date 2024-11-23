import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

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
    folder = 'texts'  
    folder_path=os.path.join(cwd,folder)

    print('Cargando textos desde la carpeta...')
    texts, filenames = load_texts_from_folder(folder_path)
    print(f'Se cargaron {len(texts)} documentos.')

    print('Creando cliente de Chroma persistente...')
    chroma_client = create_persistent_client()
    print('Cliente creado.')

    print('Creando colección en la base de datos...')
    chroma_collection = chroma_client.create_collection(name='test_collection')
    print('Colección inicializada.')

    print('Añadiendo textos a la colección...')
    add_texts_to_collection(chroma_collection, texts)
    print('Datos añadidos exitosamente.')

    print('Programa terminado.')