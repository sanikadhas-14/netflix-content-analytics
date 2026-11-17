
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide"
)

# Netflix dark theme
st.markdown("""
<style>
.stApp {
    background-color: #141414;
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
[data-testid="stMetric"] {
    background: #242424;
    padding: 15px;
    border-radius: 12px;
    border-left: 4px solid #E50914;
}
[data-testid="stMetricValue"] {
    color: #E50914;
}
section[data-testid="stSidebar"] {
    background-color: #202020;
}
</style>
""", unsafe_allow_html=True)

# Load dataset only once
if "netflix_data" not in st.session_state:
    data = pd.read_csv("netflix_titles.csv")
    data.drop_duplicates(inplace=True)

    for col in ["country", "director", "cast", "rating", "listed_in"]:
        data[col] = data[col].fillna("Unknown")

    data["date_added"] = pd.to_datetime(data["date_added"], errors="coerce")
    data["release_year"] = pd.to_numeric(data["release_year"], errors="coerce")
    data["year_added"] = data["date_added"].dt.year

    st.session_state.netflix_data = data

df = st.session_state.netflix_data.copy()

# Header
st.markdown("<h1 style='color:#E50914;'>NETFLIX</h1>", unsafe_allow_html=True)
st.subheader("Content Analytics Dashboard")
st.caption("Explore and analyse Netflix movies and TV shows.")

# Manual entry section
with st.expander("➕ Add a New Movie / TV Show", expanded=False):
    with st.form("manual_entry_form"):
        st.write("Enter new content details below:")

        title = st.text_input("Title")
        col1, col2 = st.columns(2)

        with col1:
            content_type = st.selectbox("Content Type", ["Movie", "TV Show"])
            country = st.text_input("Country", placeholder="Example: India")
            release_year = st.number_input(
                "Release Year", min_value=1900, max_value=2100, value=2025
            )

        with col2:
            genre = st.text_input(
                "Genre", placeholder="Example: Drama, Comedy"
            )
            rating = st.selectbox(
                "Rating",
                ["TV-MA", "TV-14", "TV-PG", "R", "PG-13", "PG", "G", "Not Rated"]
            )
            date_added = st.date_input("Date Added", value=date.today())

        submitted = st.form_submit_button("Add Content")

        if submitted:
            if title.strip():
                new_record = {
                    "show_id": "MANUAL-" + str(len(st.session_state.netflix_data) + 1),
                    "type": content_type,
                    "title": title.strip(),
                    "director": "Unknown",
                    "cast": "Unknown",
                    "country": country.strip() if country.strip() else "Unknown",
                    "date_added": pd.Timestamp(date_added),
                    "release_year": release_year,
                    "rating": rating,
                    "duration": "Unknown",
                    "listed_in": genre.strip() if genre.strip() else "Unknown",
                    "description": "Manually added content",
                    "year_added": date_added.year
                }

                st.session_state.netflix_data = pd.concat(
                    [st.session_state.netflix_data, pd.DataFrame([new_record])],
                    ignore_index=True
                )
                st.success("New content added successfully!")
                st.rerun()
            else:
                st.error("Please enter a title.")

# Refresh data after manual entry
df = st.session_state.netflix_data.copy()

# Sidebar filters
st.sidebar.title("Dashboard Filters")

types = ["All"] + sorted(df["type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Content Type", types)

years = sorted(df["release_year"].dropna().unique().tolist(), reverse=True)
selected_year = st.sidebar.selectbox("Release Year", ["All"] + years)

countries = sorted(df["country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Country", ["All"] + countries)

filtered = df.copy()

if selected_type != "All":
    filtered = filtered[filtered["type"] == selected_type]

if selected_year != "All":
    filtered = filtered[filtered["release_year"] == selected_year]

if selected_country != "All":
    filtered = filtered[
        filtered["country"].str.contains(selected_country, case=False, na=False)
    ]

# Dashboard metrics
st.markdown("### Dashboard Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Total Titles", len(filtered))
c2.metric("Movies", len(filtered[filtered["type"] == "Movie"]))
c3.metric("TV Shows", len(filtered[filtered["type"] == "TV Show"]))

st.divider()

# Smaller graphs in two columns
left, right = st.columns(2)

# Graph 1: Movies vs TV Shows
with left:
    st.subheader("1. Movies vs TV Shows")

    type_data = filtered["type"].value_counts().reset_index()
    type_data.columns = ["Type", "Count"]

    fig1 = px.pie(
        type_data,
        names="Type",
        values="Count",
        hole=0.5,
        color_discrete_sequence=["#E50914", "#777777"]
    )
    fig1.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#141414"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Graph 2: Top Countries
with right:
    st.subheader("2. Top 10 Countries")

    country_data = (
        filtered[filtered["country"] != "Unknown"]["country"]
        .str.split(", ").explode()
    )
    top_countries = country_data.value_counts().head(10).reset_index()
    top_countries.columns = ["Country", "Titles"]

    fig2 = px.bar(
        top_countries,
        x="Country",
        y="Titles",
        color_discrete_sequence=["#E50914"]
    )
    fig2.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#141414"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Graph 3: Content Added Over Years
with left:
    st.subheader("3. Content Added Over Years")

    year_data = (
        filtered.dropna(subset=["year_added"])["year_added"]
        .value_counts().sort_index().reset_index()
    )
    year_data.columns = ["Year", "Titles"]

    fig3 = px.line(
        year_data,
        x="Year",
        y="Titles",
        markers=True
    )
    fig3.update_traces(line_color="#E50914", marker_color="#E50914")
    fig3.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#141414"
    )
    st.plotly_chart(fig3, use_container_width=True)

# Graph 4: Genres
with right:
    st.subheader("4. Most Common Genres")

    genre_data = filtered["listed_in"].str.split(", ").explode()
    top_genres = genre_data.value_counts().head(10).reset_index()
    top_genres.columns = ["Genre", "Titles"]

    fig4 = px.bar(
        top_genres,
        x="Titles",
        y="Genre",
        orientation="h",
        color_discrete_sequence=["#E50914"]
    )
    fig4.update_layout(
        template="plotly_dark",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#141414"
    )
    st.plotly_chart(fig4, use_container_width=True)

# Dataset preview
st.divider()
st.subheader("Dataset Preview")
st.dataframe(filtered.head(20), use_container_width=True)

# Download updated dataset
st.download_button(
    "Download Updated Dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="netflix_updated.csv",
    mime="text/csv"
)

st.caption("Netflix Content Analytics | Data Wrangling and Preprocessing Project")


