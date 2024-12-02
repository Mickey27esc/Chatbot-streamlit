import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

import google.generativeai as genai

def get_relevant_passage(query, db_collection):
    passage = db_collection.query(query_texts=[query], n_results=1)['documents'][0][0]
    return passage