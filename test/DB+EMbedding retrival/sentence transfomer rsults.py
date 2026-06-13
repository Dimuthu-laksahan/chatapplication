from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sentences = ["I am pizza", "I enjoy eating pizza"]

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Get embeddings
embeddings = model.encode(sentences)

# Check similarity
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
print("Similarity:", similarity[0][0])
