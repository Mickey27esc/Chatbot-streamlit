import streamlit as st
import google.generativeai as genai
import chromadb 
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

##################################################################
# CONFIGURACIÓN DE LA BASE DE DATOS DE CHROMA

# Se crea una conexión persistente con una base de datos que ya exista
client = chromadb.PersistentClient(
        path="database",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

collection = client.get_collection(name="planes-de-estudio")

##################################################################
# FUNCIONES RAG

# Función para obtener el pasaje más relevante para una consulta
def get_relevant_passage(query, collection, n_results):
    passage = collection.query(query_texts=[query], n_results=n_results)['documents'][0]
    return passage


# Función para limpiar el texto del pasaje
def clean_passage(passage_list):
    import re
    cleaned_text = ""
    # Recorre cada pasaje y elimina caracteres innecesarios
    for passage in passage_list:
        passage.replace("'", "").replace('"', "")
        text = re.sub(r'\n(\w)', r'\1', passage)
        cleaned_text += text + " "
    return cleaned_text

# Función para crear el prompt para el modelo RAG
def make_rag_prompt(query, relevant_passage):
    escaped = clean_passage(relevant_passage)
    # Define el prompt con las instrucciones para el modelo de generación
    # Se tiene que tomar en cuenta el rol del asistente para una mejor respuesta.
    prompt = ("""Eres un asistente útil e informativo que responde preguntas sobre los planes de estudio
    de una universidad utilizando el texto del pasaje de referencia incluido a continuación. \
    
    Asegúrate de responder en una oración completa, siendo detallado y proporcionando toda la 
    información de contexto relevante. PERO SOLO RESPONDIENDO LO QUE SE PREGUNTA \
    
    Sin embargo, estás hablando con una audiencia no técnica, así que asegúrate de desglosar 
    conceptos complicados y mantener un tono amigable y conversacional. \
    
    Trata de generar una respuesta con el pasaje, lo más cercana a la pregunta realizada. \
    NO HAGAS REFERENCIA AL PASAJE EN TU RESPUESTA.
    
    Si el pasaje no es relevante para la respuesta o la información es limitada para dar una respuesta,
    responde con "No encotré información relevante para tu pregunta con la inforamción con la que cuento". \
    
    PREGUNTA: '{query}' 
    
    PASAJE: '{relevant_passage}

    RESPUESTA:
    """).format(query=query, relevant_passage=escaped)

    return prompt


##################################################################
# INTERFAZ DE USUARIO 

st.title("🤖📂 Gemini-based RAG chatbot")
st.header("Hola ¿En qué te puedo ayudar?")

# Entrada de la clave API de Gemini desde el sidebar (panel lateral)
API_KEY = st.sidebar.text_input("GEMINI API Key", type="password")
genai.configure(api_key=API_KEY)

# Inicializar el modelo de Gemini si aún no está en el estado de la sesión
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel("gemini-1.5-flash")

# Inicializar el historial de chat si aún no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Inicializar el chat si aún no existe
if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(
        history=st.session_state.chat_history,
    )
    

# Mostrar los mensajes anteriores del chat al recargar la aplicación
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Recibir la entrada del usuario para hacer una pregunta
if prompt := st.chat_input("Escribe aquí..."):
    # Añadir el mensaje del usuario al historial de chat
    st.session_state.chat_history.append(
        dict(
            role='user',
            content=prompt,
        )
    )
    # Mostrar el mensaje del usuario en el chat
    with st.chat_message("user"):
        st.markdown(prompt)
    # Mostrar la respuesta del asistente en el chat
    with st.chat_message("assistant"):   
        
        # Obtener el pasaje más relevante para la pregunta del usuario
        results = get_relevant_passage(prompt, collection, 10)
        # Crear el prompt RAG utilizando los resultados
        rag_prompt = make_rag_prompt(prompt, results)

        # Generar una respuesta con GEMINI en un formato de chat
        response = st.session_state.chat.send_message(rag_prompt)
        st.markdown(response.text)  # Mostrar respuesta
    # Añadir la respuesta de GEMINI al historial
    st.session_state.chat_history.append({"role": "assistant", "content": response.text})