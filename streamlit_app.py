import streamlit as st
from qdrant_client import QdrantClient
import numpy as np
import random
import pandas as pd

# Initialize Qdrant client using secrets from Streamlit
client = QdrantClient(api_key=st.secrets["q_api_key"], url=st.secrets["q_url"])

# Function to retrieve movie recommendations from Qdrant
def get_movie_recommendations(vectors, top_k=5):
    if len(vectors) > 0:
        average_vector = np.mean(vectors, axis=0)
    else:
        st.warning("You need to like at least one movie to get recommendations.")
        return []

    results = client.search(
        collection_name="movielens",
        query_vector=average_vector,
        limit=top_k,
    )
    return [result.payload for result in results]

# Function to fetch random movies from Qdrant collection
def get_random_movies(client, num_movies=3):
    points = client.scroll(
        collection_name="movielens",
        limit=num_movies,
    )
    return points[0]  # Returns the list of points (movies)

# Function to convert movie title to vector (assumes the vectors are already stored in Qdrant)
def get_movie_vector(movie_title, client):
    results = client.search(
        collection_name="movielens",
        query_vector=np.zeros(128),  # Dummy vector to initiate the search
        limit=1,
        query_filter={"must": [{"key": "title", "match": {"value": movie_title}}]}
    )
    return results[0].vector if results else None

# Fetching random movies from the Qdrant collection
random_movies = get_random_movies(client)

# Streamlit app UI
st.title("Movie Recommendation Engine")

# Display three random movies
liked_vectors = []
st.write("Do you like these movies?")
for movie in random_movies:
    st.write(f"**{movie['payload']['title']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"👍 Like {movie['payload']['title']}"):
            vector = get_movie_vector(movie['payload']['title'], client)
            if vector is not None:
                liked_vectors.append(vector)
    with col2:
        st.button(f"👎 Dislike {movie['payload']['title']}")

# Generate recommendations if the user liked at least one movie
if len(liked_vectors) > 0:
    st.write("Here are some movie recommendations based on your preferences:")
    recommendations = get_movie_recommendations(liked_vectors)
    for movie in recommendations:
        st.write(f"**{movie['title']}** ({movie.get('release_year', 'N/A')})")
        st.write(f"Genre: {movie.get('genre', 'N/A')}")
        st.write(f"Box Office: ${movie.get('box_office', 'N/A')}")
else:
    st.warning("Please like at least one movie to get recommendations.")
