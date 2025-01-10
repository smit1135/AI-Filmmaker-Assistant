import spacy
import pandas as pd
from datetime import datetime
import streamlit as st

# Load spaCy language model
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
    "film_length": ["feature", "short", "feature"],
    "production_stage": ["completed", "in post-production", "completed"],
    "premiere_status": ["world premiere", "previous screenings", "world premiere"],
    "geographic_focus": ["international", "national", "regional"],
    "submission_deadlines": ["early bird", "regular", "late"],
    "technical_specs": ["DCP", "ProRes", "DCP"],
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

# Ensure 'entry_fee' column is numeric
if "entry_fee" in festival_df.columns:
    festival_df["entry_fee"] = pd.to_numeric(festival_df["entry_fee"], errors='coerce')
else:
    raise KeyError("'entry_fee' column is missing from the DataFrame.")

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

# Function to recommend distribution platforms
def recommend_distribution(df, user_genre, user_type, budget, festival_count):
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
    return recommendations[:int(festival_count)]

# Function to recommend marketing strategies
def recommend_marketing(budget, creative_options, goal):
    if budget < 500:
        return [
            {"platform": "YouTube", "strategy": "Focus on organic trailer promotion."},
            {"platform": "Instagram", "strategy": "Leverage organic reels and short-form content for awareness."}
        ]
    elif budget <= 1000:
        return [
            {"platform": "YouTube", "strategy": "Combine organic trailer promotion with minimal paid ads for targeting specific audiences."},
            {"platform": "Facebook/Instagram", "strategy": "Boost posts to target specific segments, including trailer promotion or awareness campaigns."}
        ]
    else:
        return [
            {"platform": "YouTube", "strategy": "Extensive paid and organic strategy for trailer views or sales."},
            {"platform": "Facebook/Instagram", "strategy": "Launch a comprehensive paid campaign for engagement and purchases."},
            {"platform": "Google Ads", "strategy": "Use paid search ads for trailer views, preorders, or website visits."}
        ]

# Ask if the user wants a digital marketing recommendation
want_marketing_recco = st.radio("Do you want a digital marketing recommendation?", ["Yes", "No"])

if want_marketing_recco == "Yes":
    marketing_budget = st.slider("Do you have a budget set aside for marketing?", 0, 5000, 500)
    has_creatives = st.radio("Do you already have trailers, reels, or other materials?", ["Yes", "No"])
    
    if has_creatives == "Yes":
        creative_options = st.multiselect("Which materials do you have available?", ["Trailers", "Reels", "Shorts"])
    
    marketing_goal = st.selectbox("What is your marketing goal?", ["Drive trailer views", "Increase awareness", "Drive sales", "Drive website visits"])
    release_timing = st.text_input("When should the content be released?", "ASAP")

    # Get marketing recommendations
    marketing_recommendations = recommend_marketing(marketing_budget, creative_options, marketing_goal)

    # Display marketing recommendations
    st.header("Marketing Recommendations")
    for rec in marketing_recommendations:
        st.write(f"Platform: {rec['platform']}")
        st.write(f"Strategy: {rec['strategy']}")
        st.markdown("---")

# Get festival recommendations
distribution_recommendations = recommend_distribution(festival_df, user_genre, user_type, user_budget, festival_count)

# Display distribution recommendations in Streamlit
st.header("Festival Recommendations")
for rec in distribution_recommendations:
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


