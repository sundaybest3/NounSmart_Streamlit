import streamlit as st
import pandas as pd
import random

# Load the CSV file
csv_url = "https://raw.githubusercontent.com/sundaybest3/NounSmart/refs/heads/main/Irregular_Nouns.csv"
df = pd.read_csv(csv_url)

# Count the number of items in each Level
level_counts = df["Level"].value_counts()
levels_with_counts = [
    f"{level} ({level_counts.get(level, 0)} items)"
    for level in ["easy_peasy", "easy", "normal", "challenging", "superchallenging"]
]

# Initialize session state if not already set
if "state" not in st.session_state:
    st.session_state.state = {
        "nickname": None,
        "remaining_nouns": pd.DataFrame(),
        "current_level": None,
        "score": 0,
        "trials": 0,
        "current_index": -1,
        "level_scores": {level: {"score": 0, "trials": 0} for level in ["easy_peasy", "easy", "normal", "challenging", "superchallenging"]},
    }

state = st.session_state.state

# Function to reset the state when a new level is selected
def reset_level(level):
    filtered_nouns = df[df["Level"] == level].copy()
    if not filtered_nouns.empty:
        state["remaining_nouns"] = filtered_nouns
        state["current_level"] = level
        state["score"] = 0
        state["trials"] = 0
        state["current_index"] = -1
        st.success(f"Level '{level}' selected. Click 'Show the Noun' to start!")
    else:
        st.error(f"No nouns available for the Level: {level}. Please select a different level.")

# Function to show the next noun
def show_next_noun():
    if state["remaining_nouns"].empty:
        st.success(
            f"🎉 Great job, {state['nickname']}! All nouns have been answered correctly. "
            f"(Score: {state['score']}/{state['trials']})"
        )
        return
    state["current_index"] = random.randint(0, len(state["remaining_nouns"]) - 1)
    selected_noun = state["remaining_nouns"].iloc[state["current_index"]]
    st.session_state.current_noun = selected_noun["Singular"]

# Function to check the user's answer
def check_plural(user_plural):
    if state["remaining_nouns"].empty:
        st.success(
            f"🎉 Great job, {state['nickname']}! All nouns have been answered correctly. "
            f"(Score: {state['score']}/{state['trials']})"
        )
        return

    index = state["current_index"]
    if index == -1:
        st.warning("Please click 'Show the Noun' first.")
        return

    noun_data = state["remaining_nouns"].iloc[index]
    singular = noun_data["Singular"]
    correct_plural = noun_data["Plural"]

    # Update trials
    state["trials"] += 1
    state["level_scores"][state["current_level"]]["trials"] += 1

    if user_plural.lower() == correct_plural.lower():
        state["score"] += 1
        state["level_scores"][state["current_level"]]["score"] += 1
        feedback = f"✅ Correct! '{correct_plural}' is the plural form of '{singular}'. Click 'Show the Noun' to continue."
        # Remove the correctly answered noun
        state["remaining_nouns"] = state["remaining_nouns"].drop(state["remaining_nouns"].index[index])
    else:
        feedback = f"❌ Incorrect. The correct plural form is '{correct_plural}' for '{singular}'. This will appear again. Click 'Show the Noun' to continue."

    st.session_state.feedback = feedback

# Function to generate feedback when a level is completed
def generate_feedback():
    score = state["level_scores"][state["current_level"]]["score"]
    trials = state["level_scores"][state["current_level"]]["trials"]
    percentage = (score / trials) * 100 if trials > 0 else 0

    if percentage == 100:
        feedback = f"🎉 Congratulations, {state['nickname']}! You have mastered the {state['current_level']} level. Try the next level for further mastery."
    elif 80 < percentage < 100:
        feedback = f"👏 Well done, {state['nickname']}! You are close to mastering the {state['current_level']} level. A few more practices will lead you to mastery. Keep going!"
    elif 60 < percentage <= 80:
        feedback = f"👍 Good work, {state['nickname']}! You are making steady progress in the {state['current_level']} level. Keep practicing to improve further!"
    elif 40 < percentage <= 60:
        feedback = f"😊 Keep trying, {state['nickname']}! You are halfway there in the {state['current_level']} level. Practice more to strengthen your skills!"
    elif 20 < percentage <= 40:
        feedback = f"💪 Don't give up, {state['nickname']}! You're working hard on the {state['current_level']} level. Consistent effort will help you improve!"
    else:
        feedback = f"😅 Don't worry, {state['nickname']}! The {state['current_level']} level is challenging, but with persistence, you'll get better. Try again!"

    return feedback + f" (Score: {score}/{trials}, {percentage:.2f}% correct)"

# Streamlit UI
st.title("NounSmart: Practice Irregular Plural Nouns")

# Nickname input
state["nickname"] = st.text_input("Enter your nickname to start.", value=state["nickname"] or "")
if state["nickname"]:
    st.success(f"Hello, {state['nickname']}! Select a level to practice.")

# Level selection
level = st.selectbox("Select a Level", levels_with_counts)
if st.button("Set Level"):
    reset_level(level.split(" ")[0])

# Show the noun
if st.button("Show the Noun"):
    show_next_noun()

# Display the current noun
if "current_noun" in st.session_state:
    st.write(f"Singular Noun: **{st.session_state.current_noun}**")

# User input for plural form
user_plural = st.text_input("Enter the plural form:")
if st.button("Submit Answer"):
    check_plural(user_plural)
    if "feedback" in st.session_state:
        st.write(st.session_state.feedback)

# Generate and display feedback for level completion
if state["remaining_nouns"].empty and state["current_level"]:
    st.markdown(generate_feedback())

