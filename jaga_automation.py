import requests
import json
import base64
import ddddocr
import time
import os
import argparse

# Default token should be set via environment variable JAGA_AUTH_TOKEN or passed as argument
# You can extract this from your browser's developer tools (Network tab) when logged into jaga.id
DEFAULT_TOKEN = "YOUR_BEARER_TOKEN_HERE"

class JagaAutomation:
    def __init__(self, token=None):
        self.base_url = "https://jaga.id/api/v5"
        self.token = token or os.environ.get("JAGA_AUTH_TOKEN") or DEFAULT_TOKEN

        if self.token == "YOUR_BEARER_TOKEN_HERE":
             print("[!] Warning: Using placeholder token. Please provide a valid Bearer token via --token or JAGA_AUTH_TOKEN env var.")

        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Referer": "https://jaga.id/pelayanan-publik/fasilitas-kesehatan?vnk=3400046a",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"'
        }
        self.ocr = ddddocr.DdddOcr(show_ad=False)

    def get_captcha(self):
        """Request a new captcha from the server."""
        print("[*] Requesting captcha...")
        url = f"{self.base_url}/captchas/generate"
        try:
            # The body is empty JSON object
            response = requests.post(url, headers=self.headers, json={})
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                captcha_data = data["data"]
                print(f"[*] Captcha received. UUID: {captcha_data['uuid']}")
                return captcha_data
            else:
                print(f"[!] Failed to get captcha: {data}")
                return None
        except Exception as e:
            print(f"[!] Error getting captcha: {e}")
            return None

    def solve_captcha(self, base64_image):
        """Decode and solve the captcha using ddddocr."""
        print("[*] Solving captcha...")
        try:
            # Remove header if present
            if "," in base64_image:
                base64_image = base64_image.split(",")[1]

            image_bytes = base64.b64decode(base64_image)
            res = self.ocr.classification(image_bytes)
            print(f"[*] Captcha solved: {res}")
            return res
        except Exception as e:
            print(f"[!] Error solving captcha: {e}")
            return None

    def get_bpjs_detail(self, nik, tgl_lahir, captcha_uuid, captcha_answer):
        """Fetch BPJS details using the solved captcha."""
        print(f"[*] Fetching BPJS details for NIK: {nik}")
        url = f"{self.base_url}/bpjs/detail"
        params = {
            "nik": nik,
            "tgl_lahir": tgl_lahir,
            "captcha_uuid": captcha_uuid,
            "captcha_answer": captcha_answer
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            # Check if request was successful but API returned error
            try:
                data = response.json()
            except:
                print(f"[!] Response text: {response.text}")
                return

            if response.status_code == 200:
                 if data.get("success"):
                     print("[+] Success!")
                     print(json.dumps(data, indent=4))
                 else:
                     print(f"[-] API Error: {data}")
            else:
                print(f"[!] HTTP Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"[!] Error fetching details: {e}")

    def run(self, nik, tgl_lahir):
        print("--- Starting Jaga.id Automation ---")
        captcha_data = self.get_captcha()
        if captcha_data:
            uuid = captcha_data['uuid']
            image_data = captcha_data['inline_image']

            answer = self.solve_captcha(image_data)
            if answer:
                # Add a small delay to mimic human behavior
                time.sleep(1)
                self.get_bpjs_detail(nik, tgl_lahir, uuid, answer)
            else:
                print("[!] Could not solve captcha.")
        else:
            print("[!] Could not retrieve captcha.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jaga.id BPJS Detail Automation")
    parser.add_argument("--nik", required=True, help="NIK Number")
    parser.add_argument("--dob", required=True, help="Date of Birth (YYYY-MM-DD)")
    parser.add_argument("--token", help="Bearer Token (optional)")

    args = parser.parse_args()

    automation = JagaAutomation(token=args.token)
    automation.run(args.nik, args.dob)
