from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2")

loaded_index = faiss.read_index("C:\\Users\\MSI\\Desktop\\chatapplication\\test\\faiss db\\faiss_index.bin")
print("Total embeddings loaded:", loaded_index.ntotal)

# Encode query sentence
query = "I like pasta"
query_embedding = model.encode([query]).astype('float32')

# Search for 2 nearest neighbors

# Print actual sentences
sentences = ["I love pizza", "I enjoy eating pasta", "I like burgers"]


# Perform search
k = 5  # number of nearest neighbors
distances, indices = loaded_index.search(np.array(query_embedding, dtype='float32'), k)

print("Query:", query)
for i, idx in enumerate(indices[0]):
    print(f"Result {i+1}: {sentences[idx]} (Distance: {distances[0][i]:.4f})")
      