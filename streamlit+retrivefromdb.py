import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os

# Paths
FAISS_PATH = "C:\\Users\\MSI\\Desktop\\chatapplication\\test\\DB+EMbedding retrival\\faiss_index.bin"
SENTENCES_PATH = "C:\\Users\\MSI\\Desktop\\chatapplication\\test\\DB+EMbedding retrival\\sentences.npy"

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize or load FAISS index
if os.path.exists(FAISS_PATH) and os.path.exists(SENTENCES_PATH):
    index = faiss.read_index(FAISS_PATH)
    sentences = list(np.load(SENTENCES_PATH, allow_pickle=True))
    st.write(f"Loaded FAISS index with {index.ntotal} embeddings and {len(sentences)} sentences")
else:
    index = None
    sentences = []
    st.write("No FAISS index found. Add sentences below to create one.")

st.title("Semantic Search & Embedding Storage")

# --- Add sentences ---
st.subheader("Add New Sentences")
new_sentences = st.text_area("Enter sentences (one per line):")

if st.button("Add Sentences"):
    lines = [s.strip() for s in new_sentences.split("\n") if s.strip() != ""]
    if len(lines) == 0:
        st.error("Please enter at least one valid sentence.")
    else:
        # Append new sentences
        sentences.extend(lines)
        
        # Generate embeddings
        embeddings = model.encode(lines).astype('float32')
        
        # Create FAISS index if doesn't exist
        if index is None:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to FAISS
        index.add(embeddings)
        
        # Save index and sentences
        faiss.write_index(index, FAISS_PATH)
        np.save(SENTENCES_PATH, np.array(sentences))
        
        st.success(f"Added {len(lines)} sentences! Total now: {len(sentences)}")

# --- Search sentences ---
st.subheader("Search Sentences")
query = st.text_input("Enter your query:")
k = st.slider("Number of results", min_value=1, max_value=5, value=3)

if query:
    if index is not None and index.ntotal > 0:
        # Encode query
        query_embedding = model.encode([query]).astype('float32')
        
        # Search in FAISS
        distances, indices = index.search(query_embedding, k)
        
        st.subheader("Results:")
        for i, idx in enumerate(indices[0]):
            if idx < len(sentences):
                st.write(f"{i+1}. {sentences[idx]} (Distance: {distances[0][i]:.4f})")
            else:
                st.write(f"{i+1}. [Sentence not found] (Distance: {distances[0][i]:.4f})")
    else:
        st.warning("No sentences in the index yet. Add sentences first.")


#(python -m streamlit run streamlit+retrivefromdb.py)
