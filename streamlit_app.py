import streamlit as st
from qdrant_client import QdrantClient
import numpy as np
import random
import pandas as pd  

# Initialize Qdrant client
client = QdrantClient(api_key=st.secrets["q_api_key"], url=st.secrets["q_url"])  # Adjust host/port as necessary

# Function to retrieve movie recommendations from Qdrant
def get_movie_recommendations(vectors, top_k=5):
    # Average the vectors of liked movies
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

# Function to fetch random movies
def get_random_movies(movies_df, num_movies=3):
    return movies_df.sample(n=num_movies).to_dict(orient='records')

# Function to convert movie title to vector (placeholder - replace with your embedding method)
def get_movie_vector(movie_title):
    # Implement your vectorization logic here
    return np.random.random(128).astype(np.float32)  # Example: 128-dimensional float32 vector

# Load movie data
# Assuming movies_df is a DataFrame loaded from your dataset in Qdrant
# Replace this with your actual DataFrame loading code
movies_df = pd.DataFrame([{"title": "Movie A", "movie_id": 1}, {"title": "Movie B", "movie_id": 2}, {"title": "Movie C", "movie_id": 3}])

# Streamlit app UI
st.title("Movie Recommendation Engine")

# Display three random movies
random_movies = get_random_movies(movies_df)
liked_vectors = []

st.write("Do you like these movies?")
for movie in random_movies:
    st.write(f"**{movie['title']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"👍 Like {movie['title']}"):
            vector = get_movie_vector(movie['title'])
            liked_vectors.append(vector)
    with col2:
        st.button(f"👎 Dislike {movie['title']}")

# Generate recommendations if the user liked at least one movie
if len(liked_vectors) > 0:
    st.write("Here are some movie recommendations based on your preferences:")
    recommendations = get_movie_recommendations(liked_vectors)
    for movie in recommendations:
        st.write(f"**{movie['title']}** ({movie['release_year']})")
        st.write(f"Genre: {movie['genre']}")
        st.write(f"Box Office: ${movie['box_office']}")
else:
    st.warning("Please like at least one movie to get recommendations.")
