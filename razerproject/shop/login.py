import requests
import pyotp
import sys
from session_manager import RazerSessionManager
import pickle

if __name__ == "__main__":
    email = sys.argv[1]
    password = sys.argv[2]
  


# LOGIN API it will set some cookies that is used by API that return bearer 
login_url = "https://oauth2.razer.com/services/login_sso"
login_payload = {
    "grant_type": "password",
    "client_id": "63c74d17e027dc11f642146bfeeaee09c3ce23d8",
    "scope": "sso cop",
    "redirect_uri": "https://gold.razer.com",
    "username": email,
    "password": password
}
login_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

session = requests.Session()

login_response = session.post(login_url, data=login_payload, headers=login_headers)
print("Session Cookies:", session.cookies.get_dict())
print("Login Status:", login_response.status_code)
print("Login Body:", login_response.text)
print("LOGIN RESPONSE==>", login_response.json())



# Check login success
if login_response.status_code == 200 and "login_successful" in login_response.text:
    print("Login successful")
else:
    print("Login failed")
    print(login_response.text)
    exit()

# The API below will return the bearer.
sso_url = "https://oauth2.razer.com/services/sso"
sso_payload = {
    "client_id": "63c74d17e027dc11f642146bfeeaee09c3ce23d8",
    "client_key": "enZhdWx0",  
    "scope": "sso cop"
}
sso_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "Origin": "https://gold.razer.com",
    "Referer": "https://gold.razer.com"
}

sso_response = session.post(sso_url, data=sso_payload, headers=sso_headers)

# Parse access token
if sso_response.status_code == 200:
    token_data = sso_response.json()
    print("[OK] SSO Response:", token_data)
    print("Access Token:", token_data.get("access_token"))
    print("UUID:", token_data.get("uuid")) 
    RazerSessionManager.set_session(session)
    RazerSessionManager.set("access_token", token_data.get("access_token"))
    RazerSessionManager.set("uuid", token_data.get("uuid"))
    print("Current Session=>",RazerSessionManager.all())

    with open("session.pkl", "wb") as f:
     pickle.dump(session, f)

    with open("session_data.pkl", "wb") as f:
     pickle.dump(RazerSessionManager.all(), f)

    with open("user_data.pkl", "wb") as f:
     pickle.dump({"Account":token_data.get("account"),"RazerID":token_data.get("razerid")}, f)
  
else:
    print("Failed to get access token")
    print(sso_response.text)