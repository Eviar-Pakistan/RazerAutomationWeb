import pickle
import sys
import json
import re

if __name__ == "__main__":
    product = sys.argv[1]
    email = sys.argv[2]
    region = sys.argv[3]


result_data = {
        "success": False,
        "products": [],
        "error": ""
    }
# proxies = {
#     'http': 'http://198.199.86.11:8080',
#     'https': 'http://198.199.86.11:8080',
# }
# print("[Product.py] Email:",email," Product:",product)    
   
def safe_email(email):
    return re.sub('[^a-zA-Z0-9]', '_', email)

safe = safe_email(email)

# Step 1: Load session and data
with open(f"session_{safe}.pkl", "rb") as f:
    session = pickle.load(f)

with open(f"session_data_{safe}.pkl", "rb") as f:
    session_data = pickle.load(f)

access_token = session_data.get("access_token")
uuid = session_data.get("uuid")


# print("[Product.py] Access Token:",access_token)
# print("[Product.py] UUID:",uuid)

# print("Session Loaded:", session.cookies.get_dict())
# print("Access Token:", access_token)
# print("UUID:", uuid)

catalog_url = f"https://gold.razer.com/api/v2/content/gold/catalogs/{int(region)}/{product}"

catalog_headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
    "x-razer-accesstoken": access_token,
    "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",  # Replace with dynamic if needed
    "x-razer-language": "en",
    "x-razer-razerid": uuid,
    "Origin": "https://gold.razer.com",
    "Referer": "https://gold.razer.com/pk/en/gold/catalog/pubg-mobile-uc-code"
}
try:
 catalog_response = session.get(catalog_url, headers=catalog_headers)
except Exception as e:
 result_data["error"] = f"Catalog Load Failed: {str(e)}"

if catalog_response.status_code == 200:
    catalog_data = catalog_response.json()
    # print("Catalog Loaded ")
    # print("Catalog Data ==>",catalog_data["gameSkus"])
    minimal_products = [
    {"productId": sku["productId"], "vanityName": sku["vanityName"]}
    for sku in catalog_data["gameSkus"]
]
    result_data["products"] = minimal_products
    result_data["success"] = True
    print(json.dumps({"catalog_result": result_data}))
else:
    # print("Catalog Load Failed ")
    # print("Status:", catalog_response.status_code)
    # print(catalog_response.text)
    result_data["error"] = f"Catalog Load Failed: {catalog_response.text} (Status {catalog_response.status_code})"
    result_data["success"] = False
    print(json.dumps({"catalog_result": result_data}))
