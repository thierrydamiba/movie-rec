import streamlit as st
import numpy as np
from qdrant_client import QdrantClient, models
from collections import defaultdict

# Initialize Qdrant client using secrets from Streamlit
client = QdrantClient(api_key=st.secrets["q_api_key"], url=st.secrets["q_url"])

# Function to load movie titles from Qdrant
def load_movies(client):
    response = client.scroll(collection_name="movielens", limit=100)
    movies = {point.payload['movie_id']: point.payload['title'] for point in response[0]}
    return movies

movies_dict = load_movies(client)

# Convert user ratings into a Qdrant vector
def to_vector(ratings):
    vector = models.SparseVector(values=[], indices=[])
    for movie_id, rating in ratings.items():
        vector.values.append(rating)
        vector.indices.append(movie_id)
    return vector

# Streamlit app UI
st.title("Movie Recommendation Engine")

st.write("Rate some movies to get personalized recommendations:")

# Initialize a dictionary to store user ratings
user_ratings = {}

# Allow users to rate movies
for movie_id, movie_title in movies_dict.items():
    user_ratings[movie_id] = st.slider(
        f"{movie_title} ({movie_id})", min_value=-1, max_value=1, value=0
    )

# Filter out movies that haven't been rated
filtered_ratings = {movie_id: rating for movie_id, rating in user_ratings.items() if rating != 0}

# Generate recommendations when the user submits their ratings
if st.button("Get Recommendations") and filtered_ratings:
    query_vector = to_vector(filtered_ratings)
    results = client.search(
        collection_name="movielens",
        query_vector=models.NamedSparseVector(
            name="ratings",
            vector=query_vector
        ),
        with_vectors=True,
        limit=10
    )

    # Calculate movie scores based on similar users' ratings
    def results_to_scores(results):
        movie_scores = defaultdict(lambda: 0)
        for user in results:
            user_scores = user.vector['ratings']
            for idx, rating in zip(user_scores.indices, user_scores.values):
                if idx in filtered_ratings:
                    continue
                movie_scores[idx] += rating
        return movie_scores

    movie_scores = results_to_scores(results)
    top_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)

    # Display top movie recommendations
    st.write("Top recommended movies based on your ratings:")
    for movie_id, score in top_movies[:5]:
        movie_data = client.scroll(
            collection_name="movielens",
            filter={"must": [{"key": "movie_id", "match": {"value": movie_id}}]}
        )
        if movie_data[0]:
            title = movie_data[0].payload["title"]
            genres = movie_data[0].payload["genres"]
            st.write(f"{title} ({genres}): Score {score}")
else:
    st.warning("Please rate at least one movie to get recommendations.")
