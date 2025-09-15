import requests
import pyotp
import sys
import pickle
import os
import json
import random
import string


# region = {
#     "MY": 1,
#     "GLOBAL": 2,
#     "IN": 4,
#     "SG": 5,
#     "AU": 6,
#     "ID": 7,
#     "PH": 8,
#     "VN": 9,
#     "TH": 10,
#     "US": 12,
#     "BR": 13,
#     "TW": 14,
#     "NZ": 15,
#     "EU": 16,
#     "HK": 17,
#     "TR": 18,
#     "MM": 19,
#     "CA": 20,
#     "MX": 21,
#     "CO": 22,
#     "PE": 23,
#     "AR": 24,
#     "CL": 25,
#     "KH": 26,
#     "JP": 27,
#     "GLOBALZH": 28,
#     "PK": 29,
#     "BO": 30,
#     "GT": 31,
#     "KR": 32,
#     "GLOBALRU": 36,
#     "BD": 37,
# }

IP="127.0.0.1:8000"
errorString=""
# Getting data from frontend-->views.py-->main2.py
if __name__ == "__main__":
    raw_data = sys.argv[1]
    selected_products = json.loads(raw_data)
    productName = sys.argv[2] 
    userEmail=sys.argv[3]
    secretKey=sys.argv[4]
    regionId=sys.argv[5]
    print("[Main2] Selected Products:", selected_products)
    print("[Main2] Product Name:", productName)
    print("[Main2] Email Name:", userEmail)
    print("[Main2] Secret Key:", secretKey)
    print("[Main2] region:",regionId)
  
    # Loading session to get cookies etc
    with open("session.pkl", "rb") as f:
      session = pickle.load(f)



    # Loading accessToken and uuid
    with open("session_data.pkl", "rb") as f:
      session_data = pickle.load(f)
      access_token = session_data.get("access_token")
      uuid = session_data.get("uuid")

    print("Session Loaded From main2.py:", session.cookies.get_dict())
    print("Access Token  From main2.py:", access_token)
    print("UUID  From main2.py:", uuid)


    # Loading user info
    with open("user_data.pkl", "rb") as f:
      user_data=pickle.load(f)
    print("User Data",user_data)
    # Opening a file
    output_file = "results.txt"
    with open(output_file, "w") as f:
      f.write("User Details\n")
      f.write("===================\n\n")
      f.write(f"Account:{user_data.get("Account")}\n")
      f.write(f"RazerID:{user_data.get("RazerID")}\n\n")
      f.write("===================\n")
      f.write("Product Details\n")
      f.write("===================\n\n")
    #   f.write(f"Product Name:{product}\n")
    #   f.write(f"Product Type:{productVanity}\n")
    #   f.write(f"Product Quantity:{quantity}\n")


    for product in selected_products:
        product_id = product["productId"]
        vanity = product["vanityName"]
        quantity = product["quantity"]


        with open(output_file, "a") as f:
            f.write(f"Product ID: {product_id}\n")
            f.write(f"Vanity Name: {vanity}\n")
            f.write(f"Quantity: {quantity}\n\n")
            f.write("===================\n")
          
        print(f"[Main2] Product ID: {product_id}")
        print(f"[Main2] Vanity Name: {vanity}")
        print(f"[Main2] Quantity: {quantity}")
        print("-" * 30)


        # ========================================OTP========================================
        finalcode = pyotp.TOTP(f"{secretKey}").now()
        print("[MAIN2] OTP",finalcode)

        otp_url = "https://razer-otptoken-service.razer.com/totp/post"

        otp_payload = {
              "client_id": "63c74d17e027dc11f642146bfeeaee09c3ce23d8",
              "token": finalcode}
     
        otp_headers = {
             "Content-Type": "application/json",
             "Authorization": f"Bearer {access_token}",
              "Origin": "https://razerid.razer.com",
             "Referer": "https://razerid.razer.com/"
        }

        otp_response = session.post(otp_url, json=otp_payload, headers=otp_headers)
        print("[Main2] OTP Status From :", otp_response.status_code)


        if otp_response.status_code != 200:
            print("OTP Verification Failed")
            print(otp_response.text)
            errorString+=f"{"OTP ERROR:",otp_response.text}"
            with open(output_file, "a") as f:
                    f.write(f"OTP {i+1} Failed\n{otp_response.text}\n\n\n")
            break
           
        
        otp_data = otp_response.json()
        otp_token_enc = otp_data.get("otp_token_enc")
        print("[Main2] OTP Verified:", otp_token_enc)

        # Payment Checkout
        checkout_url = "https://gold.razer.com/api/webshop/checkout/gold"
        checkout_payload = {
            "productId": int(product_id),
            "regionId": int(regionId),
            "paymentChannelId": 1,
            "emailIsRequired": True,
            "email": userEmail,
            "otpToken": otp_token_enc,
            "permalink": productName,
            "personalizedInfo": [],
            "savePurchaseDetails": True
        }

        checkout_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://gold.razer.com",
            "Referer": f"https://gold.razer.com/pk/en/gold/catalog/{productName}",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
            "x-razer-accesstoken": access_token,
            "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",
            "x-razer-language": "en",
            "x-razer-razerid": uuid
            
        }
        
        

        with open(output_file, "a") as f:
         f.write("Transaction Results\n")
         f.write("===================\n\n")

        for i in range(int(quantity)):
            checkout_response = session.post(checkout_url, json=checkout_payload, headers=checkout_headers)

            
            print("Checkout Status:", checkout_response.status_code)
            print("Chechkout Response",checkout_response.text)

            if checkout_response.status_code != 200:
                print("Checkout Failed")
                print(checkout_response.text)
                errorString+=f"{checkout_response.text}"
                with open(output_file, "a") as f:
                        f.write(f"Purchase {i+1} Failed\n{checkout_response.text}\n\n\n")
                break
                #  sys.exit()

            checkout_data = checkout_response.json()
            transaction_number = checkout_data.get("transactionNumber")
            print("Purchase Successful:", transaction_number)

            # Step 4: Get Transaction Details
            webshop_url = f"https://gold.razer.com/api/webshopv2/{transaction_number}"
            api_headers = {
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
                "x-razer-language": "en",
                "x-razer-accesstoken": access_token,
                "x-razer-razerid": uuid,
                "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",
                "Referer": f"https://gold.razer.com/pk/en/gold/purchase/transaction/{transaction_number}",
                "Origin": "https://gold.razer.com"
            }

            response = session.get(webshop_url, headers=api_headers)
            if response.status_code != 200:
                print("Getting Voucher Failed")
                print(response.text)
                errorString+=f"{response.text}"
                with open(output_file, "a") as f:
                        f.write(f"Voucher {i+1} Failed\n{response.text}\n\n\n")
                break
            data = response.json()
            pin_code = data["fullfillment"]["pins"][0]["pinCode1"]

            print("Transaction Details Status:", response.status_code)
            print("Pin Code:", pin_code)
            with open(output_file,"a") as f:
                f.write(f"Purchase {i+1}:\n")
                f.write(f"Transaction Number: {transaction_number}\n")
                f.write(f"Pin Code: {pin_code}\n\n")

def generate_random_string(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

random_string = generate_random_string()
upload_url = f"http://{IP}/save-and-store-file/"

with open(output_file, "r") as f:
    file_content = f.read()

upload_payload = {
    "email": userEmail,  
    "filename": f"{random_string}.txt",
    "content": file_content
}

try:
    upload_response = requests.post(upload_url, data=upload_payload)
    if upload_response.status_code == 200:
        print("[Main2] File uploaded and stored in model")
        print(" Download URL:", upload_response.json().get("download_url"))
        if errorString:
            print("eerrorString",errorString)
    else:
        print("[Main2] Failed to upload file")
        print(upload_response.text)
except Exception as e:
    print("[Main2] Exception during file upload:", str(e))


print(f"\n All results saved in {output_file}")
print(f"Download here: http://{IP}/download-results/")

















