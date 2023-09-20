from fastapi import FastAPI
import httpx

app = FastAPI()

CLIENT_ID = "YOUR_LINKEDIN_CLIENT_ID"
CLIENT_SECRET = "YOUR_LINKEDIN_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8008/login/linkedin/callback/"
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


@app.get("/login")
async def login():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random_state_string",  # You should generate a random string for security
        "scope": "openid profile email",
    }
    url = AUTHORIZATION_URL + "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return {"login_url": url}

@app.get("/login/linkedin/callback/")
async def login_callback(code: str, state: str):
    # get user access token
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        token_data = resp.json()
    access_token = token_data["access_token"]

    # get user information
    api_url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    api_url = "https://api.linkedin.com/v2/userinfo"

    user_info = None
    async with httpx.AsyncClient() as cc:
        response = await cc.get(api_url, headers=headers)
        user_info = response.json()
        print("l59", user_info)

    return {"access_token": access_token, "user_info": user_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level='debug')