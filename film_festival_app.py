import spacy
import pandas as pd
from datetime import datetime
import streamlit as st

# Load spaCy language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Sample festival data
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
}

# Convert deadlines to datetime and then format as MM/DD/YYYY
festival_data["deadline"] = [datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d/%Y") for d in festival_data["deadline"]]

# Convert to DataFrame
festival_df = pd.DataFrame(festival_data)

# Preprocess genres and types
def preprocess_column(column):
    return [item.split(";") for item in column]

festival_df["genres"] = preprocess_column(festival_df["genres"])
festival_df["type"] = preprocess_column(festival_df["type"])

# Streamlit UI setup
st.title("Film Festival Finder and Marketing Assistant 🎥")
st.sidebar.header("About the App")
st.sidebar.info(
    "This AI Agent helps filmmakers find the best Festivals, Distribution Platforms and digital marketing strategies for their projects."
)

# User Inputs
user_genre = st.selectbox("Primary genre of your film:", ["Drama", "Comedy", "Documentary", "Sci-Fi", "Thriller"])
user_type = st.selectbox("Type of your film:", ["feature", "short", "documentary", "animation"])
user_budget = st.slider("Budget for festival entry fees ($):", 0, 500, 10)
festival_count = st.slider("Number of festival recommendations:", 1, 10, 1)

# Function to recommend festivals
def recommend_festivals(df, user_genre, user_type, budget, count):
    recommendations = []
    
    for _, row in df.iterrows():
        genre_match = user_genre in row["genres"]
        type_match = user_type in row["type"]
        budget_match = budget >= row["entry_fee"]
        deadline_match = datetime.strptime(row["deadline"], "%m/%d/%Y") >= datetime.now()

        score = int(genre_match) + int(type_match) + int(budget_match) + int(deadline_match)
        recommendations.append({
            "festival": row["festival"],
            "description": row["description"],
            "entry_fee": row["entry_fee"],
            "deadline": row["deadline"],
            "rationale": row["rationale"],
            "score": score,
        })
    
    recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)
    return recommendations[:count]

# Get festival recommendations
festival_recommendations = recommend_festivals(festival_df, user_genre, user_type, user_budget, festival_count)

# Display festival recommendations
st.header("Festival Recommendations")
for rec in festival_recommendations:
    st.subheader(f"Festival: {rec['festival']}")
    st.write(f"Description: {rec['description']}")
    st.write(f"Entry Fee: ${rec['entry_fee']}")
    st.write(f"Deadline: {rec['deadline']}")
    st.write(f"Rationale: {rec['rationale']}")
    st.markdown("---")

# Feedback prompt
st.subheader("Was this recommendation helpful?")
user_feedback = st.radio("Select an option", ["Yes", "No"])

if user_feedback == "Yes":
    st.success("We're glad you found it helpful!")
else:
    st.warning("We'll work on improving it. Thank you for your feedback!")


