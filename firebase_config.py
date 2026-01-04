import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_key = st.secrets["FIREBASE_KEY"]

    # 🔧 FIX: convert escaped newlines to real newlines
    firebase_key = firebase_key.replace("\\n", "\n")

    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred)

db = firestore.client()
