from mem0 import Memory

from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
import os
config={
    
    "version":"v1.1",
    "embedder":{
        "provider"
    }
}




vectore_store=Chroma(
    embedding_function= GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
    persist_directory='pinecon_db',
    collection_name='sample'
    
)