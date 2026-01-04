import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    # Use to_dict() method
    cred = credentials.Certificate(st.secrets["firebase"].to_dict())
    firebase_admin.initialize_app(cred)

db = firestore.client()
