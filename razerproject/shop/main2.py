import requests
import pyotp
import sys
import pickle
import os
import json
import random
import string
import re
import uuid
import traceback

def safe_email(email):
    return re.sub('[^a-zA-Z0-9]', '_', email)

def generate_random_string(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def main():
    result_data = {
        "success": False,
        "otp_success": False,
        "download_url_success": False,
        "download_url": None,
        "error": "",
        "details": []
    }

    try:
        raw_data = sys.argv[1]
        selected_products = json.loads(raw_data)
        productName = sys.argv[2] 
        userEmail = sys.argv[3]
        secretKey = sys.argv[4]
        regionId = sys.argv[5]
        output_file = sys.argv[6]
        IP = "127.0.0.1:8000"

        safe = safe_email(userEmail)

        with open(f"session_{safe}.pkl", "rb") as f:
            session = pickle.load(f)
        with open(f"session_data_{safe}.pkl", "rb") as f:
            session_data = pickle.load(f)
            access_token = session_data.get("access_token")
            uuid_val = session_data.get("uuid")
        with open(f"user_data_{safe}.pkl", "rb") as f:
            user_data = pickle.load(f)

        with open(output_file, "w") as f:
            f.write("User Details\n")
            f.write("===================\n\n")
            f.write(f"Account:{user_data.get('Account')}\n")
            f.write(f"RazerID:{user_data.get('RazerID')}\n\n")
            f.write("===================\n")
            f.write("Product Details\n")
            f.write("===================\n\n")

        for product in selected_products:
            product_id = product["productId"]
            vanity = product["vanityName"]
            quantity = product["quantity"]

            with open(output_file, "a") as f:
                f.write(f"Product ID: {product_id}\n")
                f.write(f"Vanity Name: {vanity}\n")
                f.write(f"Quantity: {quantity}\n\n")
                f.write("===================\n")

            # OTP Section
            finalcode = pyotp.TOTP(f"{secretKey}").now()
            otp_url = "https://razer-otptoken-service.razer.com/totp/post"
            otp_payload = {
                "client_id": "63c74d17e027dc11f642146bfeeaee09c3ce23d8",
                "token": finalcode
            }
            otp_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "Origin": "https://razerid.razer.com",
                "Referer": "https://razerid.razer.com/"
            }
            otp_response = session.post(otp_url, json=otp_payload, headers=otp_headers)
            if otp_response.status_code != 200:

                error_msg = f"OTP ERROR: Maybe Invalid Secret key or Expired Token"
                result_data["error"] = error_msg
                result_data["otp_success"] = False
                result_data["success"] = False

                with open(output_file, "a") as f:
                    f.write(f"OTP Failed\n{otp_response.text}\n\n\n")
                result_data["details"].append({
                    "productId": product_id,
                    "success": False,
                    "error": error_msg
                })
                break
            result_data["otp_success"] = True
            result_data["success"] = True
            otp_data = otp_response.json()
            otp_token_enc = otp_data.get("otp_token_enc")

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
                "x-razer-razerid": uuid_val
            }

            with open(output_file, "a") as f:
                f.write("Transaction Results\n")
                f.write("===================\n\n")

            for i in range(int(quantity)):
                checkout_response = session.post(checkout_url, json=checkout_payload, headers=checkout_headers)
                if checkout_response.status_code != 200:
                    error_msg = f"Checkout Failed: {checkout_response.text}"
                    result_data["error"] = error_msg
                    result_data["success"] = False

                    with open(output_file, "a") as f:
                        f.write(f"Purchase {i+1} Failed\n{checkout_response.text}\n\n\n")
                    result_data["details"].append({
                        "productId": product_id,
                        "success": False,
                        "error": error_msg
                    })
                    break
                result_data["success"] = True
                checkout_data = checkout_response.json()
                transaction_number = checkout_data.get("transactionNumber")

                # Get Transaction Details
                webshop_url = f"https://gold.razer.com/api/webshopv2/{transaction_number}"
                api_headers = {
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
                    "x-razer-language": "en",
                    "x-razer-accesstoken": access_token,
                    "x-razer-razerid": uuid_val,
                    "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",
                    "Referer": f"https://gold.razer.com/pk/en/gold/purchase/transaction/{transaction_number}",
                    "Origin": "https://gold.razer.com"
                }

                response = session.get(webshop_url, headers=api_headers)
                if response.status_code != 200:
                    error_msg = f"Voucher Failed: {response.text}"
                    result_data["error"] = error_msg
                    result_data["success"] = False
                    with open(output_file, "a") as f:
                        f.write(f"Voucher {i+1} Failed\n{response.text}\n\n\n")
                    result_data["details"].append({
                        "productId": product_id,
                        "success": False,
                        "error": error_msg
                    })
                    break
                result_data["success"] = True
                data = response.json()
                pin_code = data["fullfillment"]["pins"][0]["pinCode1"]
                with open(output_file, "a") as f:
                    f.write(f"Purchase {i+1}:\n")
                    f.write(f"Transaction Number: {transaction_number}\n")
                    f.write(f"Pin Code: {pin_code}\n\n")
                result_data["details"].append({
                    "productId": product_id,
                    "success": True,
                    "transaction_number": transaction_number,
                    "pin_code": pin_code
                })

        # Upload file to backend
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
                result_data["download_url_success"] = True
                result_data["download_url"] = upload_response.json().get("download_url")
                os.remove(output_file)
            else:
                result_data["error"] = f"Failed to upload file: {upload_response.text}"
        except Exception as e:
            result_data["error"] = f"Exception during file upload: {str(e)}"

    except Exception as e:
       result_data["error"] = str(e) + traceback.format_exc()

    print(json.dumps(result_data))

if __name__ == "__main__":
    main()