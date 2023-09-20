from fastapi import FastAPI, Request
import httpx

app = FastAPI()

CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8007/auth/"
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

@app.get("/login/google")
async def login_google(request: Request):
    # Generate a unique state for CSRF protection (optional but recommended)
    state = "random_string"
    # Store the state in the session or a database to compare later
    # store_state_in_session(state)
    # Redirect the user to Google's authorization URL
    authorization_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&response_type=code&scope=openid email"
    return {"login_url":authorization_url}


@app.get("/auth")
async def login_callback_google(code: str, state: str):
    # Handle Google callback
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    # get user access token
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        token_data = resp.json()
    access_token = token_data["access_token"]

    # get user info
    user_info = None
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        userinfo_resp.raise_for_status()
        user_info = userinfo_resp.json()
        print("l46", user_info)

    return {"access_token": access_token, "user_info": user_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007, log_level='debug')

