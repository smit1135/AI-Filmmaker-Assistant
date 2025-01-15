import openai
import spacy
import pandas as pd
from datetime import datetime
import streamlit as st

# Load the OpenAI API key
openai.api_key = "YOsk-proj-HIHaTKY5S_kZWFVKlNI49QpOjD6OaxADHHNoFtwPdoQsInz5wuiIiUizzjSk35nP54n2fFSk22T3BlbkFJOn_2UwxjOzXeIfjofogAJGC221GlW8qCqW2tUB7oiDVaA-6cDlwwxGw8pgzUSU8Ot8M7cWb3YA"

# Load spaCy language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Sample festival data with submission guidelines
festival_data = {
    "festival": ["Sundance Film Festival", "SXSW", "Tribeca Film Festival"],
    "description": [
        "A premier festival showcasing independent voices in genres like Drama and Romance.",
        "A unique festival celebrating diverse storytelling including Comedy and Documentary.",
        "A festival known for urban stories and drama, featuring cutting-edge films.",
    ],
    "type": ["feature;short", "documentary;short", "feature;drama"],
    "genres": ["Drama;Romance", "Documentary;Comedy", "Drama;Urban"],
    "entry_fee": [50, 30, 60],
    "deadline": ["2025-02-15", "2025-03-01", "2025-01-30"],
    "rationale": [
        "Known for promoting groundbreaking feature films.",
        "Well-suited for diverse storytelling in comedy and documentary genres.",
        "Highlighted for recognizing innovative urban dramas.",
    ],
    "submission_guidelines": [
        "Films must be under 40 minutes for shorts; over 40 minutes for features.",
        "Must include a completed entry form, digital screener, and payment receipt.",
        "Submissions require an artist statement and premiere status confirmation.",
    ],
}

# Updated distribution data with submission guidelines
distribution_data = {
    "platform": [
        "Netflix", "Amazon Prime", "YouTube", "Juno Films", "IFC Films",
        "Entertainment One", "Bleecker Street", "FilmRise", "Breaking Glass Pictures",
    ],
    "genres": [
        "Drama;Romance", "Documentary;Comedy", "Drama;Urban",
        "Drama;Documentary", "Drama;Comedy", "Drama;Thriller",
        "Drama;Indie", "Documentary;Drama", "LGBTQ+;Drama",
    ],
    "type": [
        "feature;short", "documentary;short", "feature;drama",
        "documentary;indie", "feature;indie", "feature;short",
        "feature;short", "documentary;short", "feature;indie",
    ],
    "rationale": [
        "Netflix is ideal for high-production-value features in Drama and Romance genres.",
        "Amazon Prime supports diverse and independent creators, particularly in documentary and comedy.",
        "YouTube is a versatile platform for urban and experimental dramas with global reach.",
        "Juno Films specializes in high-quality documentaries and unique dramas.",
        "IFC Films is known for its focus on independent and art-house films.",
        "Entertainment One distributes a wide variety of indie films and thrillers globally.",
        "Bleecker Street highlights bold, original, and critically acclaimed indie films.",
        "FilmRise is perfect for digital distribution of documentaries and indie dramas.",
        "Breaking Glass Pictures caters to diverse stories, including LGBTQ+ and indie drama.",
    ],
    "submission_guidelines": [
        "Submissions must include a finished film, press kit, and detailed synopsis.",
        "Digital screeners with subtitles for non-English content required.",
        "Films should have no online availability prior to submission.",
        "Short films must be under 30 minutes; features must be over 60 minutes.",
        "Scripts and storyboards required for partially completed films.",
        "Digital or Blu-ray screeners required with promotional assets.",
        "Content must appeal to niche audiences; full-resolution digital files required.",
        "Submit via FilmFreeway with production credits and festival history.",
        "Provide LGBTQ+ representation credentials if applicable.",
    ],
}

# Convert to DataFrames
festival_df = pd.DataFrame(festival_data)
distribution_df = pd.DataFrame(distribution_data)

# Preprocess genres and types
def preprocess_column(column):
    return [item.split(";") for item in column]

festival_df["genres"] = preprocess_column(festival_df["genres"])
festival_df["type"] = preprocess_column(festival_df["type"])
distribution_df["genres"] = preprocess_column(distribution_df["genres"])
distribution_df["type"] = preprocess_column(distribution_df["type"])

# Streamlit UI setup
st.title("Filmmaker AI Assistant 🎥")

# Function to recommend festivals
def recommend_festivals(df, user_genre, user_type, budget, count):
    recommendations = []

    for _, row in df.iterrows():
        genre_match = user_genre in row.get("genres", [])
        type_match = user_type in row.get("type", [])
        budget_match = budget >= row.get("entry_fee", 0)
        try:
            deadline_match = datetime.strptime(row.get("deadline", "01/01/1900"), "%Y-%m-%d") >= datetime.now()
        except ValueError:
            deadline_match = False

        score = int(genre_match) + int(type_match) + int(budget_match) + int(deadline_match)
        recommendations.append({
            "festival": row.get("festival", "Unknown"),
            "description": row.get("description", "No description available."),
            "entry_fee": row.get("entry_fee", "N/A"),
            "deadline": row.get("deadline", "N/A"),
            "rationale": row.get("rationale", "No rationale available."),
            "submission_guidelines": row.get("submission_guidelines", "No guidelines available."),
            "score": score,
        })

    recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)
    return recommendations[:count]

# Function to recommend distribution platforms
def recommend_distribution_platforms(df, user_genre, user_type):
    recommendations = []

    for _, row in df.iterrows():
        genre_match = user_genre in row.get("genres", [])
        type_match = user_type in row.get("type", [])
        score = int(genre_match) + int(type_match)

        if score > 0:
            recommendations.append({
                "platform": row.get("platform", "Unknown"),
                "rationale": row.get("rationale", "No rationale available."),
                "submission_guidelines": row.get("submission_guidelines", "No guidelines available."),
                "score": score,
            })

    recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)
    return recommendations

# Chatbot functionality
def chatbot_response(user_input):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You are a helpful assistant for indie filmmakers. Answer the question: {user_input}",
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].text.strip()

# Tabs for functionality
tab1, tab2, tab3 = st.tabs(["Festival Recommendations", "Distribution Platforms", "Chatbot"])

with tab1:
    user_genre = st.selectbox("Primary genre of your film:", ["Drama", "Comedy", "Documentary", "Sci-Fi", "Thriller", "LGBTQ+"])
    user_type = st.selectbox("Type of your film:", ["feature", "short", "documentary", "animation", "indie"])
    user_budget = st.slider("Budget for festival entry fees ($):", 0, 500, 10)
    festival_count = st.slider("Number of festival recommendations:", 1, 10, 1)

    st.header("Festival Recommendations")
    festival_recommendations = recommend_festivals(festival_df, user_genre, user_type, user_budget, festival_count)
    for rec in festival_recommendations:
        st.subheader(f"Festival: {rec['festival']}")
        st.write(f"Description: {rec['description']}")
        st.write(f"Entry Fee: ${rec['entry_fee']}")
        st.write(f"Deadline: {rec['deadline']}")
        st.write(f"Rationale: {rec['rationale']}")
        st.write(f"Submission Guidelines: {rec['submission_guidelines']}")
        st.markdown("---")

with tab2:
    user_genre = st.selectbox("Primary genre of your film (for distribution):", ["Drama", "Comedy", "Documentary", "Sci-Fi", "Thriller", "LGBTQ+"])
    user_type = st.selectbox("Type of your film (for distribution):", ["feature", "short", "documentary", "animation", "indie"])

    st.header("Distribution Platform Recommendations")
    distribution_recommendations = recommend_distribution_platforms(distribution_df, user_genre, user_type)
    for rec in distribution_recommendations:
        st.subheader(f"Platform: {rec['platform']}")
        st.write(f"Rationale: {rec['rationale']}")
        st.write(f"Submission Guidelines: {rec['submission_guidelines']}")
        st.markdown("---")

with tab3:
    st.header("Chatbot")
    user_input = st.text_input("Ask me anything about filmmaking:")
    if user_input:
        chatbot_reply = chatbot_response(user_input)
        st.write(chatbot_reply)


