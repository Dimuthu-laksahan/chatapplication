from sentence_transformers import SentenceTransformer
import numpy as np
import faiss


# Example sentences
sentences = ["I love pizza", "I enjoy eating pasta", "I like burgers"]

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
embeddings = model.encode(sentences)
embeddings = np.array(embeddings, dtype='float32')  # FAISS requires float32
print("Embeddings shape:", embeddings.shape)


dimension = embeddings.shape[1]  # 384 for MiniLM
index = faiss.IndexFlatL2(dimension)  # L2 distance index
index.add(embeddings)  # Add embeddings to index

print("Total embeddings in index:", index.ntotal)

faiss.write_index(index, "C:\\Users\\MSI\\Desktop\\chatapplication\\test\\faiss db\\faiss_index.bin")


