import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# ----------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Data Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NETFLIX_RED = "#E50914"
NETFLIX_BLACK = "#141414"
NETFLIX_DARKGRAY = "#221f1f"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {NETFLIX_BLACK};
        color: white;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {NETFLIX_DARKGRAY};
    }}
    h1, h2, h3, h4 {{
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
    }}
    div[data-testid="stMetric"] {{
        background-color: {NETFLIX_DARKGRAY};
        border: 1px solid {NETFLIX_RED};
        border-radius: 8px;
        padding: 15px 10px;
    }}
    div[data-testid="stMetricValue"] {{
        color: {NETFLIX_RED};
    }}
    .netflix-title {{
        color: {NETFLIX_RED};
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }}
    .netflix-subtitle {{
        color: #b3b3b3;
        font-size: 16px;
        margin-top: 0px;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Netflix-themed template for all Plotly charts
PLOTLY_TEMPLATE = go.layout.Template()
PLOTLY_TEMPLATE.layout = go.Layout(
    paper_bgcolor=NETFLIX_BLACK,
    plot_bgcolor=NETFLIX_BLACK,
    font=dict(color="white"),
    xaxis=dict(gridcolor="#333333"),
    yaxis=dict(gridcolor="#333333"),
)

# ----------------------------------------------------------------------------
# DATA LOADING & CLEANING (cached so it only runs once, not on every filter)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_movies.csv")

    # Handle missing values
    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    mode_country = df["country"].mode()[0]
    df["country"] = df["country"].fillna(mode_country)
    df.dropna(subset=["date_added", "rating", "duration"], inplace=True)

    # Transformations
    df["date_added"] = pd.to_datetime(df["date_added"], format="mixed", dayfirst=False)
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month
    df["age_on_netflix"] = df["year_added"] - df["release_year"]

    # Split duration into minutes (movies) / seasons (TV shows)
    movies_mask = df["type"] == "Movie"
    tv_mask = df["type"] == "TV Show"
    df.loc[movies_mask, "duration_min"] = (
        df.loc[movies_mask, "duration"].str.replace(" min", "", regex=False).astype(float)
    )
    df.loc[tv_mask, "seasons"] = (
        df.loc[tv_mask, "duration"]
        .str.replace(" Seasons", "", regex=False)
        .str.replace(" Season", "", regex=False)
        .astype(float)
    )

    # Explode multi-value columns for genre/country analysis
    df["genre_list"] = df["listed_in"].str.split(", ")
    df["country_list"] = df["country"].str.split(", ")

    return df


df = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🎛️ Filters")

content_type = st.sidebar.multiselect(
    "Content Type", options=sorted(df["type"].unique()), default=list(df["type"].unique())
)

all_genres = sorted(set(g for sub in df["genre_list"] for g in sub))
genre_filter = st.sidebar.multiselect("Genre", options=all_genres, default=[])

all_countries = sorted(set(c for sub in df["country_list"] for c in sub))
country_filter = st.sidebar.multiselect("Country", options=all_countries, default=[])

min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider(
    "Release Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year)
)

# ----------------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------------
filtered = df[
    df["type"].isin(content_type)
    & df["release_year"].between(year_range[0], year_range[1])
]

if genre_filter:
    filtered = filtered[filtered["genre_list"].apply(lambda lst: any(g in lst for g in genre_filter))]

if country_filter:
    filtered = filtered[filtered["country_list"].apply(lambda lst: any(c in lst for c in country_filter))]

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown('<p class="netflix-title">NETFLIX DATA ANALYSIS DASHBOARD</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="netflix-subtitle">Exploring trends across ~8,800 Netflix titles — content type, genre, ratings, and geography</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ----------------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------------
if len(filtered) == 0:
    st.warning("No titles match the current filters. Try widening your selection.")
    st.stop()

total_titles = filtered.shape[0]
type_ratio = filtered["type"].value_counts(normalize=True) * 100
movie_pct = type_ratio.get("Movie", 0)
avg_duration = filtered.loc[filtered["type"] == "Movie", "duration_min"].mean()
top_country = filtered["country"].value_counts().idxmax() if not filtered.empty else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", f"{total_titles:,}")
col2.metric("Movies Share", f"{movie_pct:.1f}%")
col3.metric("Avg Movie Duration", f"{avg_duration:.0f} min" if not np.isnan(avg_duration) else "N/A")
col4.metric("Top Country", top_country)

st.markdown("---")

# ----------------------------------------------------------------------------
# ROW 1: Content type pie + Growth over time
# ----------------------------------------------------------------------------
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.subheader("Movies vs TV Shows")
    type_counts = filtered["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig = px.pie(
        type_counts, names="type", values="count",
        color="type", color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#B3B3B3"},
        hole=0.4,
    )
    fig.update_traces(textinfo="percent+label", textfont_color="white")
    fig.update_layout(template=PLOTLY_TEMPLATE, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.subheader("Content Added Over the Years")
    trend = filtered.groupby(["year_added", "type"]).size().reset_index(name="count")
    fig = px.line(
        trend, x="year_added", y="count", color="type", markers=True,
        color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#B3B3B3"},
    )
    fig.update_layout(template=PLOTLY_TEMPLATE, xaxis_title="Year Added", yaxis_title="Titles Added")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# ROW 2: Top genres + Top countries
# ----------------------------------------------------------------------------
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.subheader("Top 10 Genres")
    genres_exp = filtered.explode("genre_list")
    top_genres = genres_exp["genre_list"].value_counts().head(10).reset_index()
    top_genres.columns = ["genre", "count"]
    fig = px.bar(
        top_genres.sort_values("count"), x="count", y="genre", orientation="h",
        color_discrete_sequence=[NETFLIX_RED],
    )
    fig.update_layout(template=PLOTLY_TEMPLATE, xaxis_title="Count", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    st.subheader("Top 10 Content-Producing Countries")
    countries_exp = filtered.explode("country_list")
    top_countries = countries_exp["country_list"].value_counts().head(10).reset_index()
    top_countries.columns = ["country", "count"]
    fig = px.bar(
        top_countries.sort_values("count"), x="count", y="country", orientation="h",
        color_discrete_sequence=[NETFLIX_RED],
    )
    fig.update_layout(template=PLOTLY_TEMPLATE, xaxis_title="Count", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# ROW 3: Ratings + Duration distribution
# ----------------------------------------------------------------------------
r3c1, r3c2 = st.columns(2)

with r3c1:
    st.subheader("Content Ratings Distribution")
    rating_counts = filtered["rating"].value_counts().reset_index()
    rating_counts.columns = ["rating", "count"]
    fig = px.bar(rating_counts, x="rating", y="count", color_discrete_sequence=[NETFLIX_RED])
    fig.update_layout(template=PLOTLY_TEMPLATE, xaxis_title="Rating", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with r3c2:
    st.subheader("Movie Duration Distribution")
    movie_durations = filtered[filtered["type"] == "Movie"]["duration_min"].dropna()
    fig = px.histogram(movie_durations, nbins=50, color_discrete_sequence=[NETFLIX_RED])
    fig.update_layout(
        template=PLOTLY_TEMPLATE, xaxis_title="Duration (minutes)", yaxis_title="Count", showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# ROW 4: Word cloud
# ----------------------------------------------------------------------------
st.subheader("Most Common Words in Content Descriptions")
text = " ".join(filtered["description"].dropna())
if text.strip():
    wc = WordCloud(
        width=1200, height=400, background_color=NETFLIX_BLACK,
        colormap="Reds", stopwords=STOPWORDS,
    ).generate(text)
    fig, ax = plt.subplots(figsize=(15, 5))
    fig.patch.set_facecolor(NETFLIX_BLACK)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

st.markdown("---")
st.caption("Built with Streamlit · Data: Netflix Titles Dataset · Dashboard by Arijit")
