import streamlit as st
import os

st.title("📂 Bestanden in jouw Streamlit Cloud omgeving")

for root, dirs, files in os.walk(".", topdown=True):
    for name in files:
        st.write(os.path.join(root, name))
