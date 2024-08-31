import streamlit as st
from qdrant_client import QdrantClient

# Initialize Qdrant client using secrets from Streamlit
client = QdrantClient(api_key=st.secrets["q_api_key"], url=st.secrets["q_url"])

# Load movies from Qdrant
def load_movies(client):
    response = client.scroll(collection_name="movielens", limit=10)
    
    # Check if data is retrieved
    if not response[0]:
        st.error("No data retrieved from the Qdrant collection.")
        return {}
    
    st.write(f"Retrieved {len(response[0])} points from Qdrant.")

    # Initialize an empty dictionary to store movie titles
    movies = {}
    
    # Iterate through each user point
    for point in response[0]:
        st.write(f"User ID: {point.payload['user_id']}, Movies Rated: {len(point.payload['movies_rated'])}")
        
        # Iterate through each movie in the user's movies_rated list
        for movie in point.payload.get("movies_rated", []):
            st.write(f"Found movie: {movie['title']} with ID: {movie['movie_id']}")  # Debugging line
            movies[movie["movie_id"]] = movie["title"]
    
    st.write(f"Total movies loaded: {len(movies)}")  # Debugging line
    
    return movies

movies_dict = load_movies(client)

# Streamlit app UI
st.title("Movie Recommendation Engine")

if not movies_dict:
    st.warning("No movies available to rate. Please check the Qdrant collection.")
else:
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
                filter={"must": [{"key": "movies_rated.movie_id", "match": {"value": movie_id}}]}
            )
            if movie_data[0]:
                # Since movie_data[0] contains the user data, we need to find the movie within the movies_rated list
                movie_info = next((m for m in movie_data[0].payload["movies_rated"] if m["movie_id"] == movie_id), None)
                if movie_info:
                    title = movie_info["title"]
                    genres = movie_info["genres"]
                    st.write(f"{title} ({genres}): Score {score}")
    else:
        st.warning("Please rate at least one movie to get recommendations.")
