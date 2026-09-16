import hashlib
import hmac
import os

from src.database import get_connection


DEFAULT_USERNAME = "admin"
_PASSWORD_SALT = b"credit-rating-system-login"
_USER_PASSWORD_SALT = b"credit-rating-system-user-login"


# Verifies the administrator username and password using a PBKDF2-derived hash.
# Uses a constant-time comparison to reduce timing-based password disclosure.
def authenticate_admin(username, password):
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), _PASSWORD_SALT, 200_000
    )
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password_hash FROM admins WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()
    return row is not None and hmac.compare_digest(password_hash.hex(), row[0])


def ensure_admin_account():
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT username FROM admins WHERE username = ?", (DEFAULT_USERNAME,)
        ).fetchone()
        if row is None:
            password_hash = hashlib.pbkdf2_hmac(
                "sha256", b"password", _PASSWORD_SALT, 200_000
            ).hex()
            conn.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                (DEFAULT_USERNAME, password_hash),
            )
            conn.commit()
    finally:
        conn.close()


def change_admin_password(username, current_password, new_password):
    if not authenticate_admin(username, current_password) or not new_password:
        return False
    conn = get_connection()
    try:
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", new_password.encode("utf-8"), _PASSWORD_SALT, 200_000
        ).hex()
        conn.execute(
            "UPDATE admins SET password_hash = ? WHERE username = ?",
            (password_hash, username),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def hash_user_password(password):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), _USER_PASSWORD_SALT, 200_000
    ).hex()


def generate_user_password(first_name, last_name):
    return f"{first_name}{last_name}123".replace(" ", "").lower()


def authenticate_user(email, password):
    normalized_email = email.strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT user_id, first_name, last_name, password_hash FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or row[3] is None:
        return None
    if not hmac.compare_digest(hash_user_password(password), row[3]):
        return None
    return {
        "user_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": normalized_email,
    }


def change_user_password(user_id, current_password, new_password):
    if not new_password:
        return False
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row is None or not hmac.compare_digest(hash_user_password(current_password), row[0]):
            return False
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (hash_user_password(new_password), user_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def set_user_password(user_id, new_password):
    if not new_password:
        return False
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (hash_user_password(new_password), user_id),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()


def ensure_user_passwords():
    conn = get_connection()
    generated = []
    try:
        rows = conn.execute(
            "SELECT user_id, first_name, last_name, email FROM users WHERE password_hash IS NULL"
        ).fetchall()
        for user_id, first_name, last_name, email in rows:
            password = generate_user_password(first_name, last_name)
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE user_id = ?",
                (hash_user_password(password), user_id),
            )
            generated.append((email, password))
        conn.commit()
    finally:
        conn.close()

    if generated:
        project_root = os.path.dirname(os.path.dirname(__file__))
        credentials_path = os.path.join(project_root, "data", "user_credentials.csv")
        with open(credentials_path, "a", encoding="utf-8", newline="") as credentials_file:
            if credentials_file.tell() == 0:
                credentials_file.write("email,password\n")
            for email, password in generated:
                credentials_file.write(f"{email},{password}\n")
    return generated


def authenticate(username, password):
    """Keep the original admin authentication API available to callers."""
    return authenticate_admin(username, password)