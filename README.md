# Netflix Data Analysis And Visualisation 🎬

An exploratory data analysis (EDA) project on Netflix's catalog of \~8,800 movies and TV shows, uncovering trends in content type, genre, release patterns, ratings, and geographic distribution using Python.

* ## Project Overview

This project analyzes a dataset of 8,807 Netflix titles to answer key questions:

* How has Netflix's content library grown over time?
* What's the split between Movies and TV Shows?
* Which genres and countries dominate the catalog?
* How are content ratings distributed?
* What themes appear most in content descriptions?
* ## &#x20;Tools \& Libraries
* **Python** — Pandas, NumPy
* **Visualization** — Matplotlib, Seaborn, WordCloud
* **Environment** — Jupyter Notebook
* ## &#x20;Dataset

The dataset (`netflix\_movies.csv`) contains 8,807 titles with attributes including `title`, `director`, `cast`, `country`, `date\_added`, `release\_year`, `rating`, `duration`, and `listed\_in` (genre).

* ## Key Steps
1. **Data Loading \& Preview** — initial inspection of shape, dtypes, and structure
2. **Data Cleaning \& Transformation** — handled missing values (`fillna` for director/cast, mode imputation for country, dropped negligible nulls in date\_added/rating/duration), converted `date\_added` to datetime, engineered `year\_added` and `month\_added`
3. **Exploratory Data Analysis** — content type distribution, growth over time, top genres, duration/season distributions, top content-producing countries, rating distribution, content age on Netflix
4. **Multivariate Analysis** — movie duration across top genres
5. **Text Analysis** — word cloud from content descriptions
6. **KPIs** — total titles, movie/TV ratio, average movie duration, top content-producing country
* ## Key Findings
* Netflix's catalog is **movie-heavy (\~70%)**, with content additions accelerating sharply between 2016–2019, followed by a dip likely linked to COVID-19's impact on production.
* **International Movies** is the most common genre, reflecting Netflix's global content strategy.
* Movie runtimes cluster around **90–100 minutes**; the vast majority of TV shows have just **1 season**, pointing to a preference for limited series over long-running formats.
* The **US** is the top content-producing country, followed by **India**.
* Content skews toward **mature audiences** (TV-MA, TV-14 are the most common ratings).
* A large share of titles are added the same year they're released (Netflix Originals), alongside a long tail of older licensed content.
* ## &#x20;Repository Structure

```
netflix-data-analysis/
├── Netflix\_DataAnalysis.ipynb   # Main analysis notebook
├── netflix\_movies.csv           # Dataset
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies
```

* ## &#x20;How to Run

```bash
git clone https://github.com/<your-username>/netflix-data-analysis.git
cd netflix-data-analysis
pip install -r requirements.txt
jupyter notebook Netflix\_DataAnalysis.ipynb
```

* ## &#x20;Requirements

```
pandas
numpy
matplotlib
seaborn
wordcloud
jupyter
```

* ## &#x20;Author

Arijit
Dashboard Link : https://netflixdataanalysis-visualisation-jmvqksybvt54en4kby3wvs.streamlit.app/
