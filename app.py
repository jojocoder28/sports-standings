import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Constants
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
CSV_FILE = "sports_standings.csv"

# Initialize data
def initialize_data():
    categories = {
        "Boys A": ["100m Run", "200m Run", "Long Jump"],
        "Girls A": ["100m Run", "High Jump"],
        "Boys B": ["400m Run", "High Jump"],
        "Girls B": ["200m Run", "Long Jump"],
        "Boys C": ["100m Run", "400m Run"],
        "Girls C": ["High Jump", "Long Jump"],
        "CWSN": ["50m Walk", "Ball Throw"]
    }
    if not os.path.exists(CSV_FILE):
        data = {
            "Event": [],
            "Category": [],
            "1st Place": [],
            "2nd Place": [],
            "3rd Place": []
        }
        for category, events in categories.items():
            for event in events:
                data["Event"].append(event)
                data["Category"].append(category)
                data["1st Place"].append("")
                data["2nd Place"].append("")
                data["3rd Place"].append("")
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)

# Load data
def load_data():
    return pd.read_csv(CSV_FILE)

# Save data
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Admin page
def admin_page():
    st.title("Admin Dashboard - Manage Standings and Events")
    password = st.text_input("Enter admin password:", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        df = load_data()
        st.write("Current Standings:")
        st.dataframe(df)

        # Edit standings
        st.subheader("Update Event Standings")
        category = st.selectbox("Select Category:", df["Category"].unique().tolist())
        event = st.selectbox("Select Event:", df[df["Category"] == category]["Event"].unique().tolist())
        row = df[(df["Category"] == category) & (df["Event"] == event)].index[0]
        first_place = st.text_input("1st Place:", df.loc[row, "1st Place"])
        second_place = st.text_input("2nd Place:", df.loc[row, "2nd Place"])
        third_place = st.text_input("3rd Place:", df.loc[row, "3rd Place"])

        if st.button("Update Standings"):
            df.loc[row, "1st Place"] = first_place
            df.loc[row, "2nd Place"] = second_place
            df.loc[row, "3rd Place"] = third_place
            save_data(df)
            st.success("Standings updated successfully!")

        # Add new events
        st.subheader("Add New Event")
        new_event = st.text_input("Enter new event name:")
        new_category = st.selectbox("Select Category:", df["Category"].unique().tolist(), key=42)
        if st.button("Add Event"):
            if new_event and not ((df["Event"] == new_event) & (df["Category"] == new_category)).any():
                new_row = pd.DataFrame({
                    "Event": [new_event],
                    "Category": [new_category],
                    "1st Place": [""],
                    "2nd Place": [""],
                    "3rd Place": [""]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success(f"Event '{new_event}' added successfully to category '{new_category}'!")
            elif ((df["Event"] == new_event) & (df["Category"] == new_category)).any():
                st.warning("This event already exists in the selected category!")
            else:
                st.error("Event name cannot be empty.")

        # Delete events
        st.subheader("Delete Event")
        delete_category = st.selectbox("Select Category to Delete Event From:", df["Category"].unique().tolist())
        delete_event = st.selectbox("Select Event to Delete:", df[df["Category"] == delete_category]["Event"].unique().tolist())
        if st.button("Delete Event"):
            if delete_event:
                df = df[~((df["Event"] == delete_event) & (df["Category"] == delete_category))]
                save_data(df)
                st.success(f"Event '{delete_event}' deleted successfully from category '{delete_category}'!")
    else:
        if password:
            st.error("Incorrect password!")

# User page
def user_page():
    st.title("🏆 Circle Sports for Primary Schools, 2025")
    st.subheader("Diamond Harbour North Circle")
    st.subheader("View the latest standings for all events below.")

    # Load data
    df = load_data()

    # Display the leaderboard category-wise
    categories = df["Category"].unique()
    for category in categories:
        st.write(f"### {category} Leaderboard")
        category_df = df[df["Category"] == category]

        # Style the leaderboard
        def highlight_places(val, place):
            if val:
                if place == 1:
                    return "background-color: gold; color: black; font-weight: bold;"
                elif place == 2:
                    return "background-color: silver; color: black; font-weight: bold;"
                elif place == 3:
                    return "background-color: #cd7f32; color: black; font-weight: bold;"
            return ""

        styled_df = (
            category_df.style
            .applymap(lambda val: highlight_places(val, 1), subset=["1st Place"])
            .applymap(lambda val: highlight_places(val, 2), subset=["2nd Place"])
            .applymap(lambda val: highlight_places(val, 3), subset=["3rd Place"])
        )

        # Display the leaderboard
        st.write(styled_df)

# Main app
def main():
    st.sidebar.title("Sports Event Standings")
    page = st.sidebar.radio("Select a page:", ["User View", "Admin View"])

    # Initialize data
    initialize_data()

    # Navigate pages
    if page == "User View":
        user_page()
    elif page == "Admin View":
        admin_page()

if __name__ == "__main__":
    main()
