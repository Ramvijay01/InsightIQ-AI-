

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global variables
vectorizer = None
text_chunks = []


def create_vector_store(text):

    global vectorizer, text_chunks

    # Split into chunks
    text_chunks = text.split("\n")

    # Limit chunks
    text_chunks = text_chunks[:1000]

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    vectorizer.fit(text_chunks)

    return {
        "status": "ready"
    }


def retrieve_relevant_data(vector_store, query):

    global vectorizer, text_chunks

    if not vectorizer:
        return ""

    # Transform query
    query_vector = vectorizer.transform([query])

    # Transform text
    text_vectors = vectorizer.transform(text_chunks)

    # Similarity
    similarities = cosine_similarity(
        query_vector,
        text_vectors
    ).flatten()

    # Top results
    top_indices = similarities.argsort()[-5:][::-1]

    results = []

    for idx in top_indices:

        results.append(text_chunks[idx])

    return "\n".join(results)