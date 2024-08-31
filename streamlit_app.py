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
        user_id = point.payload.get('user_id', 'Unknown ID')
        movies_rated = point.payload.get('movies_rated', None)
        
        if movies_rated is None:
            st.write(f"User ID: {user_id} has no rated movies.")
            continue
        
        st.write(f"User ID: {user_id}, Movies Rated: {len(movies_rated)}")
        
        # Iterate through each movie in the user's movies_rated list
        for movie in movies_rated:
            st.write(f"Found movie: {movie['title']} with ID: {movie['movie_id']}")
            movies[movie["movie_id"]] = movie["title"]
    
    st.write(f"Total movies loaded: {len(movies)}")
    
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
            with_vectors=Tru
