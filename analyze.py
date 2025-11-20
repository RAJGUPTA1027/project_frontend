import matplotlib
matplotlib.use('Agg')   # important for server / no-GUI
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import numpy as np
import os

def safe_savefig(fig, path):
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)

def run_analysis(csv_path, output_dir):
    df = pd.read_csv(csv_path)

    df = df.dropna(subset=['type', 'rating', 'country', 'duration', 'listed_in'], how='any')

    created = []

    # ---------------------------------------------------------
    # 1 - Movies vs TV Shows
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(6,4), dpi=100)
    df['type'].value_counts().plot(kind='bar', color=['skyblue','orange'])
    plt.title("Movies vs TV Shows"); plt.xlabel("Type"); plt.ylabel("Count")
    p = os.path.join(output_dir, '01_movies_vs_tvshows.png')
    safe_savefig(fig, p); created.append('01_movies_vs_tvshows.png')

    # ---------------------------------------------------------
    # 2 - Ratings pie
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(6,4), dpi=100)
    df['rating'].fillna('Unknown').value_counts().plot(
        kind='pie', autopct='%1.1f%%', startangle=90
    )
    plt.title("Content Ratings Distribution"); plt.ylabel('')
    p = os.path.join(output_dir, '02_ratings_pie.png')
    safe_savefig(fig, p); created.append('02_ratings_pie.png')

    # ---------------------------------------------------------
    # 3 - Movie duration histogram
    # ---------------------------------------------------------
    Movies = df[df['type'] == "Movie"].copy()
    if not Movies.empty and Movies['duration'].dtype == object:
        Movies['duration_int'] = Movies['duration'].str.replace(
            ' min','', regex=False
        ).str.extract(r'(\d+)').astype(float)
    else:
        Movies['duration_int'] = pd.to_numeric(Movies.get('duration', pd.Series()), errors='coerce')

    fig = plt.figure(figsize=(6,4), dpi=100)
    plt.hist(Movies['duration_int'].dropna(), bins=30, edgecolor='black')
    plt.title("Distribution of Movie Durations"); plt.xlabel("Minutes"); plt.ylabel("Count")
    p = os.path.join(output_dir, '03_movie_duration.png')
    safe_savefig(fig, p); created.append('03_movie_duration.png')

    # ---------------------------------------------------------
    # 4 - Releases per year scatter
    # ---------------------------------------------------------
    if 'release_year' in df.columns:
        years = df['release_year'].value_counts().sort_index()
        fig = plt.figure(figsize=(6,4), dpi=100)
        plt.scatter(years.index, years.values, color='red')
        plt.plot(years.index, years.values, color='black')
        plt.title("Number of Releases per Year"); plt.xlabel("Year"); plt.ylabel("Count")
        p = os.path.join(output_dir, '04_release_trend.png')
        safe_savefig(fig, p); created.append('04_release_trend.png')

    # ---------------------------------------------------------
    # 5 - Top countries
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(6,4), dpi=100)
    df['country'].fillna('Unknown').value_counts().head(10).plot(
        kind='barh', color='teal'
    )
    plt.xlabel("Number of Shows"); plt.title("Top 10 Countries by Netflix Content")
    p = os.path.join(output_dir, '05_top_countries.png')
    safe_savefig(fig, p); created.append('05_top_countries.png')

    # ---------------------------------------------------------
    # 6 - Genres
    # ---------------------------------------------------------
    genre_list = df['listed_in'].dropna().str.split(", ").explode()
    top_genres = genre_list.value_counts().head(15)

    fig = plt.figure(figsize=(6,4), dpi=100)
    sns.barplot(x=top_genres.values, y=top_genres.index, palette="viridis")
    plt.title("Top 15 Genres on Netflix"); plt.xlabel("Count")
    p = os.path.join(output_dir, '06_genre_analysis.png')
    safe_savefig(fig, p); created.append('06_genre_analysis.png')

    # ---------------------------------------------------------
    # 7 - WordCloud cast
    # ---------------------------------------------------------
    try:
        cast_text = " ".join(df['cast'].dropna().astype(str).tolist())
        if cast_text.strip():
            wc = WordCloud(
                width=600, height=300, background_color="black",
                stopwords=set(STOPWORDS)
            ).generate(cast_text)
            fig = plt.figure(figsize=(6,4), dpi=100)
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.title("Cast Word Cloud")
            p = os.path.join(output_dir, '07_cast_wordcloud.png')
            safe_savefig(fig, p); created.append('07_cast_wordcloud.png')
    except Exception as e:
        print("WordCloud cast error:", e)

    # ---------------------------------------------------------
    # 8 - WordCloud directors
    # ---------------------------------------------------------
    try:
        director_text = " ".join(df['director'].dropna().astype(str).tolist())
        if director_text.strip():
            wc2 = WordCloud(
                width=600, height=300, background_color="black",
                stopwords=set(STOPWORDS)
            ).generate(director_text)
            fig = plt.figure(figsize=(6,4), dpi=100)
            plt.imshow(wc2, interpolation="bilinear")
            plt.axis("off")
            plt.title("Director Word Cloud")
            p = os.path.join(output_dir, '08_director_wordcloud.png')
            safe_savefig(fig, p); created.append('08_director_wordcloud.png')
    except Exception as e:
        print("WordCloud director error:", e)

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    summary = {
        'total_rows': int(len(df)),
        'movies': int((df['type']=='Movie').sum()),
        'tv_shows': int((df['type']=='TV Show').sum()) if 'TV Show' in df['type'].unique() else 0,
        'unique_countries': int(df['country'].nunique()),
        'top_genres': top_genres.head(5).to_dict()
    }

    return summary

