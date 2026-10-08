import streamlit as st
import sqlite3
import hashlib
import re


DB_NAME = "users.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def valid_identifier(identifier):
    identifier = identifier.strip()

    # Email
    if re.match(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        identifier
    ):
        return True

    # Phone number
    if re.match(r"^\+?[0-9]{10,15}$", identifier):
        return True

    return False


def create_user(identifier, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (identifier, password)
            VALUES (?, ?)
            """,
            (
                identifier.strip(),
                hash_password(password)
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def check_user(identifier, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE identifier = ? AND password = ?
        """,
        (
            identifier.strip(),
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user is not None


def login_page():

    st.title("🔐 AQPredict Login")
    st.write("AI-Based Air Quality Prediction System")

    login_tab, signup_tab = st.tabs([
        "Login",
        "Create Account"
    ])

    with login_tab:

        identifier = st.text_input(
            "Email or Phone Number",
            key="login_identifier"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not identifier or not password:
                st.warning(
                    "Please enter your email/phone and password."
                )

            elif not valid_identifier(identifier):
                st.error(
                    "Please enter a valid email or phone number."
                )

            elif check_user(identifier, password):

                st.session_state["logged_in"] = True
                st.session_state["identifier"] = identifier

                st.rerun()

            else:
                st.error(
                    "Invalid email/phone or password."
                )

    with signup_tab:

        identifier = st.text_input(
            "Email or Phone Number",
            key="signup_identifier"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not identifier or not password:
                st.warning(
                    "Please fill all fields."
                )

            elif not valid_identifier(identifier):
                st.error(
                    "Enter a valid email or phone number."
                )

            elif len(password) < 6:
                st.error(
                    "Password must be at least 6 characters."
                )

            elif password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            elif create_user(identifier, password):

                st.success(
                    "Account created successfully! "
                    "Please login."
                )

            else:
                st.error(
                    "This email/phone is already registered."
                )


def logout():

    if st.button("Logout"):

        st.session_state["logged_in"] = False
        st.session_state["identifier"] = ""

        st.rerun()


create_users_table()