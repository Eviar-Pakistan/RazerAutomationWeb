import pickle
import sys
import json
import re

if __name__ == "__main__":
    email = sys.argv[1]

result_data = {
    "success": False,
    "balance": None,
    "gold_balance": None,
    "silver_balance": None,
    "silver":None,
    "error": ""
}

def safe_email(email):
    return re.sub('[^a-zA-Z0-9]', '_', email)

safe = safe_email(email)

# Load session and session data
with open(f"session_{safe}.pkl", "rb") as f:
    session = pickle.load(f)

with open(f"session_data_{safe}.pkl", "rb") as f:
    session_data = pickle.load(f)

access_token = session_data.get("access_token")
uuid = session_data.get("uuid")

balance_url = "https://gold.razer.com/api/gold/balance"

balance_headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
    "x-razer-accesstoken": access_token,
    "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",  # Replace if needed
    "x-razer-language": "en",
    "x-razer-razerid": uuid,
    "Origin": "https://gold.razer.com",
    "Referer": "https://gold.razer.com"
}

try:
    balance_response = session.get(balance_url, headers=balance_headers)
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        result_data["balance"] = balance_data
        result_data["gold_balance"] = balance_data.get("walletGold").get("totalGold")

        result_data["success"] = True
    else:
        result_data["error"] = f"Balance Load Failed: {balance_response.text} (Status {balance_response.status_code})"
except Exception as e:
    result_data["error"] = f"Balance Load Exception: {str(e)}"

silver_url = "https://gold.razer.com/api/silver/wallet"

headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
            "x-razer-accesstoken": access_token,
            "x-razer-fpid": "2be064edd5de4341630162d333f10e07",  # Replace if dynamic
            "x-razer-language": "en",
            "x-razer-razerid": uuid,
            "Origin": "https://gold.razer.com",
            "Referer": "https://gold.razer.com/"
}
try:
    silver_response = session.get(silver_url, headers=headers)
    if silver_response.status_code == 200:
        silver_data = silver_response.json()
        result_data["silver"] = silver_data
        result_data["silver_balance"] = silver_data.get("WalletSilver").get("BonusSilver")
        result_data["success"] = True
    else:
        result_data["error"] = f"Silver Load Failed: {silver_response.text} (Status {silver_response.status_code})"

except Exception as e:
    result_data["error"] = f"Silver Load Exception: {str(e)}"




print(json.dumps({"balance_result": result_data}))