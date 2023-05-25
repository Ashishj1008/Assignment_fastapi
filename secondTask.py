import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from datetime import timedelta, datetime
from typing import Optional
import mysql.connector

app = FastAPI()

# Configure MySQL connection
mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ashish@987456123",
    database="AUTHENTICATION"
)

# HTTP Basic authentication
security = HTTPBasic()

# Session timeout
SESSION_TIMEOUT_MINUTES = 30


def get_current_time() -> datetime:
    return datetime.now()


def authenticate_user(credentials: HTTPBasicCredentials) -> bool:
    # Get username and password from the credentials
    username = credentials.username
    password = credentials.password

    # Query the database to validate the user
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM login_page WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()

    if result and result[0] == 1:
        return True
    else:
        return False


@app.post("/user")
def create_user(username: str, password: str):
    # Check if the username is already taken
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM login_page WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and result[0] > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Insert the new user into the database
    cursor.execute("INSERT INTO login_page (username, password) VALUES (%s, %s)", (username, password))
    mysql_connection.commit()

    return {"message": "User created successfully"}


@app.post("/login")
def login(credentials: HTTPBasicCredentials):
    if authenticate_user(credentials):
        # Generate session token
        session_token = f"{credentials.username}_{get_current_time().timestamp()}"

        # Store the session token in the database
        cursor = mysql_connection.cursor()
        cursor.execute("INSERT INTO sessions (username, session_token) VALUES (%s, %s)",
                       (credentials.username, session_token))
        mysql_connection.commit()

        return {"message": "Login successful", "session_token": session_token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.get("/protected", response_class=HTMLResponse)
def protected_page(session_token: Optional[str] = None, credentials: HTTPBasicCredentials = Depends(security)):
    if session_token:
        # Check if the session token is valid and not expired
        cursor = mysql_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE session_token=%s", (session_token,))
        result = cursor.fetchone()

        if result and result[0] == 1:
            return HTMLResponse(content="<h1>Protected Page</h1>", status_code=status.HTTP_200_OK)

    if authenticate_user(credentials):
        # Generate session token
        session_token = f"{credentials.username}_{get_current_time().timestamp()}"

        # Store the session token in the database
        cursor = mysql_connection.cursor()
        cursor.execute("INSERT INTO sessions (username, session_token) VALUES (%s, %s)",
                       (credentials.username, session_token))
        mysql_connection.commit()

        response = HTMLResponse(content="<h1>Protected Page</h1>", status_code=status.HTTP_200_OK)
        response.set_cookie("session_token", session_token, max_age=SESSION_TIMEOUT_MINUTES * 60)
        return response

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


if __name__ == "__main__":
    uvicorn.run(app, port=9000)
