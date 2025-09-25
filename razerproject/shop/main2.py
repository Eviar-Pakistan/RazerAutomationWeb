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
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

with open("Debug_File.txt", "w") as f:
        f.write("Debug Starts here\n")

def safe_email(email):
    return re.sub('[^a-zA-Z0-9]', '_', email)

def generate_random_string(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def get_random_headers():
    """
    Generate random headers for better reliability
    """
    user_agents = [
        # === CHROME BROWSERS (Different Versions) ===
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # === MAC CHROME ===
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # === FIREFOX BROWSERS ===
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
        
        # === SAFARI BROWSERS ===
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        
        # === EDGE BROWSERS ===
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        
        # === LINUX BROWSERS ===
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

def fetch_raw_proxies(max_proxies=500):
    """
    Fetch more raw proxies - prioritize quality over quantity
    """
    sources = [
        {
            "name": "GeoNode HTTP",
            "url": "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
            "type": "http"
        },
        {
            "name": "GeoNode SOCKS",
            "url": "https://proxylist.geonode.com/api/proxy-list?limit=300&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
            "type": "socks"
        }
    ]
    
    all_proxies = []
    
    for source in sources:
        try:
            print(f"Fetching from {source['name']}...", file=sys.stderr)
            headers = get_random_headers()
            response = requests.get(source["url"], headers=headers, timeout=15)
            data = response.json()
            
            for proxy_data in data.get("data", []):
                ip = proxy_data.get("ip")
                port = proxy_data.get("port")
                protocols = proxy_data.get("protocols", [])
                uptime = proxy_data.get("upTime", 0)
                google = proxy_data.get("google", False)
                
                # Stricter filtering for better proxies
                min_uptime = 90 if source["type"] == "http" else 85
                
                if ip and port and uptime > min_uptime:
                    if source["type"] == "http" and "http" in protocols:
                        proxy_url = f"http://{ip}:{port}"
                    elif source["type"] == "socks" and "socks5" in protocols:
                        proxy_url = f"socks5://{ip}:{port}"
                    else:
                        continue
                    
                    all_proxies.append({
                        'http': proxy_url,
                        'https': proxy_url,
                        'source': source["name"],
                        'uptime': uptime,
                        'google': google
                    })
                    
                    if len(all_proxies) >= max_proxies:
                        break
        except Exception as e:

            with open("Debug_File.txt", "a") as f:
                f.write("Fetching Raw Proxies\n")
                f.write(f"Error fetching from {source['name']}: {e}\n")
            print(f"Error fetching from {source['name']}: {e}", file=sys.stderr)
            continue
    
    # Sort by uptime (best first)
    all_proxies.sort(key=lambda x: x['uptime'], reverse=True)
    random.shuffle(all_proxies)  # Then shuffle to avoid patterns
    print(f"Fetched {len(all_proxies)} high-quality raw proxies", file=sys.stderr)
    return all_proxies

def test_single_proxy(proxy, test_timeout=5):
    """
    Test a single proxy with slightly longer timeout
    """
    test_urls = [
        "https://httpbin.org/ip",
    ]
    
    for test_url in test_urls:
        try:
            headers = get_random_headers()
            start = time.time()
            response = requests.get(test_url, proxies=proxy, timeout=test_timeout, headers=headers)
            elapsed = time.time() - start
            
            if response.status_code == 200 and elapsed < 8:  # Fast proxies only
                return True
          
        except Exception:
            
            continue
    return False

def validate_proxies_parallel(raw_proxies, max_workers=20, target_working=80):
    """
    Get more working proxies with faster validation
    """
    print(f"Validating {len(raw_proxies)} proxies with {max_workers} workers...", file=sys.stderr)
    working_proxies = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all proxy tests
        future_to_proxy = {
            executor.submit(test_single_proxy, proxy): proxy 
            for proxy in raw_proxies
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                if future.result():  # Proxy is working
                    working_proxies.append(proxy)
                    print(f"✓ Working proxy #{len(working_proxies)}: {proxy['http'][:30]}... (uptime: {proxy['uptime']}%)", file=sys.stderr)
                    
                    # Stop when we have enough working proxies
                    if len(working_proxies) >= target_working:
                        print(f"Found {target_working} working proxies, stopping validation", file=sys.stderr)
                        # Cancel remaining futures
                        for remaining_future in future_to_proxy:
                            remaining_future.cancel()
                        break
                        
            except Exception as e:
                with open("Debug_File.txt", "a") as f:
                    f.write("Validating Proxies\n")
                    f.write(f"Error validating proxy {proxy['http']}: {e}\n")
                pass  # Silent fail for faster validation
    
    print(f"Validation complete: {len(working_proxies)} working proxies found", file=sys.stderr)
    return working_proxies

def get_validated_proxies(target_proxies=80):
    """
    Get more working proxies for better distribution
    """
    print("=== PROXY VALIDATION PHASE ===", file=sys.stderr)
    
    # Step 1: Fetch more raw proxies
    raw_proxies = fetch_raw_proxies(max_proxies=500)
    
    if not raw_proxies:
        print("No raw proxies fetched!", file=sys.stderr)
        return []
    
    # Step 2: Validate proxies in parallel
    working_proxies = validate_proxies_parallel(
        raw_proxies, 
        max_workers=20, 
        target_working=target_proxies
    )
    
    print(f"=== VALIDATION COMPLETE: {len(working_proxies)} working proxies ===", file=sys.stderr)
    return working_proxies

class ProxyManager:
    """
    Thread-safe proxy manager that ensures each worker gets unique proxy
    """
    def __init__(self, proxies):
        self.proxies = proxies.copy()
        self.used_proxies = set()
        self.lock = threading.Lock()
        self.current_index = 0
        
    def get_unique_proxy(self, worker_id):
        """
        Get a unique proxy for each worker
        """
        with self.lock:
            if not self.proxies:
                return None
                
            # Ensure each worker gets a different proxy
            proxy_index = (worker_id * 3 + self.current_index) % len(self.proxies)
            proxy = self.proxies[proxy_index]
            self.current_index += 1
            
            return proxy
            
    def mark_proxy_failed(self, proxy):
        """
        Mark a proxy as failed and get a replacement
        """
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
            
    def get_fresh_proxy(self):
        """
        Get a fresh proxy (avoiding recently used ones)
        """
        with self.lock:
            available = [p for p in self.proxies if p not in self.used_proxies]
            if not available:
                # Reset if all used
                self.used_proxies.clear()
                available = self.proxies
                
            if available:
                proxy = random.choice(available)
                self.used_proxies.add(proxy)
                # Keep only last 20 used proxies in memory
                if len(self.used_proxies) > 20:
                    self.used_proxies = set(list(self.used_proxies)[-20:])
                return proxy
            return None

def perform_purchase_optimized(i, session, checkout_url, checkout_payload_base, base_headers, access_token, uuid_val, proxy_manager, secret_key, user_email, product_name, region_id):
    """
    Optimized purchase function with better proxy handling and timing
    """
    max_retries = 2
    retry_count = 0
    
    # Get unique proxy for this worker
    proxy = proxy_manager.get_unique_proxy(i)
    
    while retry_count <= max_retries:
        try:
            # Add small staggered delay to avoid thundering herd
            stagger_delay = (i % 20) * 0.05  # 0-1 second spread
            time.sleep(stagger_delay)
            
            # Generate fresh OTP for THIS specific purchase
            fresh_otp_code = pyotp.TOTP(f"{secret_key}").now()
            
            # Get fresh OTP token
            otp_url = "https://razer-otptoken-service.razer.com/totp/post"
            otp_payload = {
                "client_id": "63c74d17e027dc11f642146bfeeaee09c3ce23d8",
                "token": fresh_otp_code
            }
            otp_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "Origin": "https://razerid.razer.com",
                "Referer": "https://razerid.razer.com/"
            }
            
            otp_response = session.post(otp_url, json=otp_payload, headers=otp_headers)
            if otp_response.status_code != 200:
                return {
                    "index": i,
                    "success": False,
                    "error": f"OTP Failed: {otp_response.text[:100]}..."
                }
            
            otp_data = otp_response.json()
            fresh_otp_token = otp_data.get("otp_token_enc")
            
            if not fresh_otp_token:
                return {
                    "index": i,
                    "success": False,
                    "error": "OTP Failed: No token received"
                }
            
            # Generate dynamic headers for this request
            dynamic_headers = get_random_headers()
            
            # Build checkout payload with fresh OTP
            checkout_payload = {
                **checkout_payload_base,
                "otpToken": fresh_otp_token,
                "email": user_email,
                "regionId": int(region_id),
                "permalink": product_name
            }
            
            # Merge with base headers
            enhanced_checkout_headers = {
                **base_headers["checkout_headers"],
                **dynamic_headers
            }
            
            proxy_info = proxy['http'][:30] + "..." if proxy else 'DIRECT'
            if retry_count > 0:
                print(f"Purchase {i+1} RETRY #{retry_count} via {proxy_info}", file=sys.stderr)
            else:
                print(f"Purchase {i+1} via {proxy_info}", file=sys.stderr)
            
            # Checkout request
            checkout_response = session.post(
                checkout_url,
                json=checkout_payload,
                headers=enhanced_checkout_headers,
                timeout=25,
                proxies=proxy
            )
            
            if checkout_response.status_code != 200:
                error_text = checkout_response.text
                
                # Check if it's Access Denied error and retry with different proxy
                if "Access Denied" in error_text and retry_count < max_retries:
                    retry_count += 1
                    print(f"Access Denied for purchase {i+1}, switching proxy (retry {retry_count})", file=sys.stderr)
                    
                    # Mark current proxy as failed and get fresh one
                    if proxy:
                        proxy_manager.mark_proxy_failed(proxy)
                    proxy = proxy_manager.get_fresh_proxy()
                    
                    # Wait before retry
                    time.sleep(random.uniform(0.5, 1.5))
                    continue
                else:
                    return {
                        "index": i,
                        "success": False,
                        "error": f"Checkout Failed: {error_text[:150]}..."
                    }

            checkout_data = checkout_response.json()
            transaction_number = checkout_data.get("transactionNumber")
            if not transaction_number:
                return {
                    "index": i,
                    "success": False,
                    "error": "Checkout Failed: Missing transactionNumber"
                }

            # Build per-transaction headers
            api_headers = {
                **dynamic_headers,
                "x-razer-language": "en",
                "x-razer-accesstoken": access_token,
                "x-razer-razerid": uuid_val,
                "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",
                "Referer": f"https://gold.razer.com/pk/en/gold/purchase/transaction/{transaction_number}",
                "Origin": "https://gold.razer.com"
            }

            # Small delay before voucher request
            time.sleep(random.uniform(0.1, 0.3))

            # Transaction details
            webshop_url = f"https://gold.razer.com/api/webshopv2/{transaction_number}"
            response = session.get(webshop_url, headers=api_headers, timeout=25, proxies=proxy)
            
            if response.status_code != 200:
                return {
                    "index": i,
                    "success": False,
                    "error": f"Voucher Failed: {response.text[:150]}..."
                }

            data = response.json()
            try:
                pin_code = data["fullfillment"]["pins"][0]["pinCode1"]
            except Exception:
                return {
                    "index": i,
                    "success": False,
                    "error": "Voucher Failed: Unable to parse pin code"
                }

            return {
                "index": i,
                "success": True,
                "transaction_number": transaction_number,
                "pin_code": pin_code,
                "proxy_used": proxy['http'] if proxy else 'DIRECT',
                "retries": retry_count
            }

        except Exception as e:
            error_msg = str(e)
            
            # Retry on proxy/connection errors
            if ("ProxyError" in error_msg or "ConnectTimeout" in error_msg or "ReadTimeout" in error_msg) and retry_count < max_retries:
                retry_count += 1
                print(f"🔌 Connection error for purchase {i+1}, switching proxy (retry {retry_count})", file=sys.stderr)
                
                # Get fresh proxy
                if proxy:
                    proxy_manager.mark_proxy_failed(proxy)
                proxy = proxy_manager.get_fresh_proxy()
                
                time.sleep(random.uniform(0.5, 1.5))
                continue
            else:
                return {
                    "index": i,
                    "success": False,
                    "error": error_msg[:150] + "..." if len(error_msg) > 150 else error_msg
                }
    
    return {
        "index": i,
        "success": False,
        "error": f"Failed after {max_retries} retries"
    }

def main():
    result_data = {
        "success": False,
        "otp_success": False,
        "download_url_success": False,
        "download_url": None,
        "error": "",
        "details": [],
        "proxiesavailable": [],
        "working_proxies_count": 0
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

        # STEP 1: Get high-quality validated proxies
        WORKING_PROXIES = get_validated_proxies(target_proxies=80)
        result_data["proxiesavailable"] = [
            {"proxy": p['http'], "source": p['source'], "uptime": p['uptime']} 
            for p in WORKING_PROXIES
        ]
        result_data["working_proxies_count"] = len(WORKING_PROXIES)
        
        if not WORKING_PROXIES:
            print("No working proxies found, will use direct connection", file=sys.stderr)
            WORKING_PROXIES = [None]

        print(f"=== STARTING RAZER OPERATIONS WITH {len(WORKING_PROXIES)} PROXIES ===", file=sys.stderr)

        # Initialize Proxy Manager for unique proxy distribution
        proxy_manager = ProxyManager(WORKING_PROXIES)

        for product in selected_products:
            product_id = product["productId"]
            vanity = product["vanityName"]
            quantity = int(product["quantity"])

            with open(output_file, "a") as f:
                f.write(f"Product ID: {product_id}\n")
                f.write(f"Vanity Name: {vanity}\n")
                f.write(f"Quantity: {quantity}\n\n")
                f.write("===================\n")

            result_data["otp_success"] = True

            # Payment Checkout base
            checkout_url = "https://gold.razer.com/api/webshop/checkout/gold"
            checkout_payload_base = {
                "productId": int(product_id),
                "paymentChannelId": 1,
                "emailIsRequired": True,
                "personalizedInfo": [],
                "savePurchaseDetails": True
            }
            
            # Base headers
            base_checkout_headers = get_random_headers()
            checkout_headers = {
                **base_checkout_headers,
                "Content-Type": "application/json",
                "Origin": "https://gold.razer.com",
                "Referer": f"https://gold.razer.com/pk/en/gold/catalog/{productName}",
                "x-razer-accesstoken": access_token,
                "x-razer-fpid": "75fd9b3d0dc92baec93a15a10f0ad247",
                "x-razer-language": "en",
                "x-razer-razerid": uuid_val
            }

            with open(output_file, "a") as f:
                f.write("Transaction Results\n")
                f.write("===================\n\n")

            base_headers = {"checkout_headers": checkout_headers}

            # STEP 2: Execute purchases with optimized settings
            max_workers = 10  # As requested
            futures = []
            start_time = time.time()

            print(f"Starting {quantity} purchases with {max_workers} workers", file=sys.stderr)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for i in range(quantity):
                    futures.append(
                        executor.submit(
                            perform_purchase_optimized,
                            i,
                            session,
                            checkout_url,
                            checkout_payload_base,
                            base_headers,
                            access_token,
                            uuid_val,
                            proxy_manager,
                            secretKey,
                            userEmail,
                            productName,
                            regionId
                        )
                    )

                successful_purchases = 0
                access_denied_count = 0
                total_retries = 0
                
                for future in as_completed(futures):
                    result = future.result()
                    i = result["index"]

                    if result["success"]:
                        successful_purchases += 1
                        result_data["success"] = True
                        proxy_used = result.get("proxy_used", "unknown")
                        retries = result.get("retries", 0)
                        total_retries += retries
                        
                        retry_info = f" (after {retries} retries)" if retries > 0 else ""
                        with open(output_file, "a") as f:
                            f.write(f"Purchase {i+1}: SUCCESS{retry_info} (via {proxy_used[:30]}...)\n")
                            f.write(f"Transaction Number: {result['transaction_number']}\n")
                            f.write(f"Pin Code: {result['pin_code']}\n\n")
                        
                        result_data["details"].append({
                            "productId": product_id,
                            "success": True,
                            "transaction_number": result["transaction_number"],
                            "pin_code": result["pin_code"],
                            "proxy_used": proxy_used,
                            "retries": retries
                        })
                    else:
                        error_msg = result["error"]
                        if "Access Denied" in error_msg:
                            access_denied_count += 1
                            
                        with open(output_file, "a") as f:
                            f.write(f"Purchase {i+1} Failed\n{error_msg}\n\n")
                            f.write(f"Transaction Number: {result.get('transaction_number', 'No transaction number')}\n")
                            f.write(f"Pin Code: {result.get('pin_code', 'No pin code')}\n\n")
                            f.write("-------------------\n")

                            
                        result_data["details"].append({
                            "productId": product_id,
                            "success": False,
                            "error": error_msg
                        })

            elapsed_time = time.time() - start_time
            success_rate = (successful_purchases / quantity) * 100
            
            with open(output_file, "a") as f:
                f.write(f"Completed {quantity} purchases in {elapsed_time:.2f}s\n")
                f.write(f"Success: {successful_purchases}/{quantity} ({success_rate:.1f}%)\n")
                f.write(f"Access Denied errors: {access_denied_count}\n")
                f.write(f"Total retries: {total_retries}\n")
                f.write("===================\n")

            print(f"Results: {successful_purchases}/{quantity} successful ({success_rate:.1f}%) in {elapsed_time:.2f}s", file=sys.stderr)
            print(f"Access Denied: {access_denied_count}, Retries: {total_retries}", file=sys.stderr)

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