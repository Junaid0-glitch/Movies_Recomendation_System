import pickle
import streamlit as st
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header styling */
    .title-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .title-container h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Movie card styling */
    .movie-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .movie-title {
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        text-align: center;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 50px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
    }
    
    .loading-text {
        font-size: 1.2rem;
        color: #667eea;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 0.5rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recommendations_count' not in st.session_state:
    st.session_state.recommendations_count = 0
if 'last_movie' not in st.session_state:
    st.session_state.last_movie = None

@st.cache_data
def load_data():
    """Load movie data with caching"""
    try:
        movies = pickle.load(open('movie_list.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError:
        st.error("⚠️ Required data files not found! Please ensure 'movie_list.pkl' and 'similarity.pkl' are in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        st.stop()

def fetch_poster(movie_id):
    """Fetch movie poster with error handling"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            # Return a placeholder image if no poster is available
            return "https://via.placeholder.com/500x750/667eea/ffffff?text=No+Poster+Available"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750/667eea/ffffff?text=Loading+Error"
    except Exception:
        return "https://via.placeholder.com/500x750/667eea/ffffff?text=No+Image"

def fetch_posters_parallel(movie_ids):
    """Fetch multiple posters in parallel for faster loading"""
    posters = [None] * len(movie_ids)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {executor.submit(fetch_poster, movie_id): i 
                          for i, movie_id in enumerate(movie_ids)}
        
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                posters[index] = future.result()
            except Exception:
                posters[index] = "https://via.placeholder.com/500x750/667eea/ffffff?text=Error"
    
    return posters

def recommend(movie, movies, similarity):
    """Get movie recommendations"""
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_movie_names = []
        movie_ids = []
        
        for i in distances[1:6]:
            movie_ids.append(movies.iloc[i[0]].movie_id)
            recommended_movie_names.append(movies.iloc[i[0]].title)
        
        # Fetch posters in parallel for faster loading
        recommended_movie_posters = fetch_posters_parallel(movie_ids)
        
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        st.error("⚠️ Movie not found in database!")
        return [], []
    except Exception as e:
        st.error(f"⚠️ Error generating recommendations: {str(e)}")
        return [], []

# Main App
def main():
    # Header with gradient background
    st.markdown("""
    <div class="title-container">
        <h1>🎬 Movie Recommender System</h1>
        <p class="subtitle">Discover your next favorite movie with AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('🎬 Loading movie database...'):
        movies, similarity = load_data()
    
    # Statistics Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-number">{len(movies):,}</div>
                <div class="stat-label">Movies Available</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-number">5</div>
                <div class="stat-label">Recommendations per Search</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-number">{st.session_state.recommendations_count}</div>
                <div class="stat-label">Total Recommendations Made</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Movie selection
    st.markdown("### 🔍 Select a Movie")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        movie_list = movies['title'].values
        selected_movie = st.selectbox(
            "Type or select a movie from the dropdown",
            movie_list,
            help="Start typing to filter the movie list"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        recommend_button = st.button('🎯 Get Recommendations', use_container_width=True)
    
    # Show recommendations
    if recommend_button:
        if selected_movie:
            st.session_state.last_movie = selected_movie
            st.session_state.recommendations_count += 1
            
            # Create a placeholder for loading animation
            loading_placeholder = st.empty()
            
            # Show loading animation
            with loading_placeholder.container():
                st.markdown("""
                <div class="loading-container">
                    <div class="loading-text">
                        🎬 Finding perfect matches for "{}"...
                    </div>
                </div>
                """.format(selected_movie), unsafe_allow_html=True)
                
                # Progress bar for visual feedback
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Small delay for animation effect
                    progress_bar.progress(i + 1)
            
            # Get recommendations
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
            
            # Clear loading animation
            loading_placeholder.empty()
            
            if recommended_movie_names:
                st.markdown("### 🎯 Recommended Movies")
                st.markdown(f"Based on your selection of **{selected_movie}**, you might also enjoy:")
                
                # Display recommendations in a responsive grid
                cols = st.columns(5)
                
                for idx, (col, name, poster) in enumerate(zip(cols, recommended_movie_names, recommended_movie_posters)):
                    with col:
                        with st.container():
                            # Movie card with hover effect
                            st.markdown(f"""
                            <div class="movie-card">
                                <img src="{poster}" style="width: 100%; border-radius: 10px 10px 0 0;">
                                <div class="movie-title">{name}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add a small spacing
                            st.markdown("<br>", unsafe_allow_html=True)
                
                # Success message
                st.success(f"✅ Found {len(recommended_movie_names)} great recommendations for you!")
                
                # Additional features
                with st.expander("💡 Want more recommendations?"):
                    st.info("Try selecting one of the recommended movies above to discover even more great films!")
            else:
                st.warning("😔 Sorry, couldn't find recommendations for this movie. Please try another one.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>🎬 Movie Recommender System | Powered by Machine Learning</p>
        <p style="font-size: 0.9rem;">Data provided by The Movie Database (TMDb)</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
