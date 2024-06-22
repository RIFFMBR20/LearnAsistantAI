import generate as gnt
import streamlit as st

st.title("Team Name Generator")

game_type = st.sidebar.selectbox("Select Game Type", ("Valorant", "Dota 2", "Mobile Legends", "CS:GO", "League of Legends", "Overwatch"))

language = st.sidebar.selectbox("Select Language", ("English", "Japanese", "Chinese", "Indonesian" ))

response = gnt.generator_team_name(game_type, language)
st.text(response)