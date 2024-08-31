import streamlit as st
from qdrant_client import QdrantClient
import numpy as np

# Initialize Qdrant client
client = QdrantClient(api_key=st.secrets["q_api_key"], url=st.secrets["q_url"])  # Adjust host/port as necessary

# Function to retrieve movie recommendations from Qdrant
def get_movie_recommendations(vector, top_k=5):
    results = client.search(
        collection_name="movielens",
        query_vector=vector,
        limit=top_k,
    )
    return [result.payload for result in results]

# Function to convert movie title to vector (placeholder - replace with your embedding method)
def get_movie_vector(movie_title):
    # Implement your vectorization logic here
    return np.random.random(128)  # Example: random vector for demonstration

# Streamlit app UI
st.title("Movie Recommendation Engine")

# User inputs a movie title
selected_movie = st.text_input("Enter a movie title you like")

if selected_movie:
    # Convert the selected movie title into a vector
    vector = get_movie_vector(selected_movie)

    # Retrieve recommendations from Qdrant
    recommendations = get_movie_recommendations(vector)

    # Display the recommendations
    st.write("Here are some movie recommendations:")
    for movie in recommendations:
        st.write(f"**{movie['title']}** ({movie['release_year']})")
        st.write(f"Genre: {movie['genre']}")
        st.write(f"Box Office: ${movie['box_office']}")
