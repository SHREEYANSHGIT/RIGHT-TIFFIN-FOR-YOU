import streamlit as st
from firebase_config import db
import hashlib
import uuid


def _hash_password(password: str, salt: str | None = None) -> str:
    """Return a salted SHA-256 hash in the form 'salt$hash'."""
    if salt is None:
        salt = uuid.uuid4().hex
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


def _verify_password(stored: str, provided: str) -> bool:
    try:
        salt, h = stored.split("$", 1)
    except Exception:
        return False
    return hashlib.sha256((salt + provided).encode("utf-8")).hexdigest() == h


def register_user():
    st.subheader("📝 Register")

    email = st.text_input("Email")
    name = st.text_input("Full Name")
    location = st.text_input("Location")
    role = st.selectbox("Role", ["Student", "Tiffin Provider"])
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not email or not name or not password:
            st.error("Name, email and password are required")
            return
        if password != confirm:
            st.error("Passwords do not match")
            return

        # check if email already exists
        existing = list(db.collection("users").where("email", "==", email).stream())
        if existing:
            st.error("Email already registered. Please login or use another email.")
            return

        hashed = _hash_password(password)
        db.collection("users").add({
            "email": email,
            "name": name,
            "location": location,
            "role": role,
            "password": hashed,
        })
        st.success("Registered successfully. Please login.")


def login_user():
    st.subheader("🔐 Login")
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        users = db.collection("users").where("email", "==", email).stream()
        found = False
        for u in users:
            found = True
            ud = u.to_dict()
            stored = ud.get("password", "")
            if stored and _verify_password(stored, password):
                st.session_state["role"] = ud.get("role")
                st.session_state["email"] = email
                st.session_state["user_id"] = u.id
                st.success("Login successful")
                return
            else:
                st.error("Wrong email or password")
                return

        if not found:
            st.error("User not found")
