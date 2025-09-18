# 🎬 Movie Recommender System

Discover your next favorite movie with this AI-powered recommender system built using Streamlit, pandas, scikit-learn, and Sentence Transformers.

## Features
- Select a movie and get 5 personalized recommendations
- Beautiful, modern UI with responsive design
- Movie posters fetched from TMDb API
- Fast recommendations using cosine similarity and sentence embeddings
- Parallel poster fetching for speed
- Caching for efficient data loading

## How It Works
- Movie metadata is preprocessed and vectorized using Sentence Transformers
- Cosine similarity is computed between movie tag vectors
- The app displays the top 5 most similar movies with posters

## Setup Instructions
1. **Clone or download this repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Prepare data files**:
   - Place `movie_list.pkl` and `similarity.pkl` in the project directory (generated from the notebook)
4. **Run the app**:
   ```bash
   streamlit run app.py
   ```
5. **Open in browser**:
   - Visit [http://localhost:8501](http://localhost:8501)

## Data Sources
- [TMDb 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-dataset)
- Movie posters via [TMDb API](https://www.themoviedb.org/documentation/api)

## File Structure
- `app.py` — Streamlit web app
- `recomendation_system.ipynb` — Data cleaning, feature engineering, and model creation
- `movie_list.pkl`, `similarity.pkl` — Preprocessed data for recommendations
- `requirements.txt` — Python dependencies

## Customization
- Change the number of recommendations by editing the code in `app.py`
- Update the UI with your own CSS in the markdown section

## License
This project is for educational purposes. Data provided by TMDb.

---
Made with ❤️ using Streamlit and Machine Learning.
