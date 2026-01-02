#!/usr/bin/env python3
"""
BPJS Checker - Manual Captcha Input
Versi tanpa OCR, user input captcha secara manual
"""

import requests
import base64
import json
import time
from datetime import datetime
import sys


class BPJSCheckerManual:
    def __init__(self, bearer_token):
        """
        Inisialisasi BPJS Checker
        
        Args:
            bearer_token: Bearer token untuk authorization
        """
        self.base_url = "https://jaga.id/api/v5"
        self.bearer_token = bearer_token
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://jaga.id/pelayanan-publik/fasilitas-kesehatan',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        })
        
    def generate_captcha(self):
        """
        Generate captcha dari API
        
        Returns:
            tuple: (captcha_uuid, captcha_image_base64) atau (None, None) jika gagal
        """
        try:
            url = f"{self.base_url}/captchas/generate"
            response = self.session.post(url, json={})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    captcha_data = data.get('data', {})
                    uuid = captcha_data.get('uuid')
                    inline_image = captcha_data.get('inline_image')
                    
                    print(f"✓ Captcha generated: {uuid}")
                    return uuid, inline_image
            
            print(f"✗ Failed to generate captcha: {response.status_code}")
            return None, None
            
        except Exception as e:
            print(f"✗ Error generating captcha: {e}")
            return None, None
    
    def save_captcha_image(self, inline_image, filename='captcha.jpg'):
        """
        Simpan captcha image ke file
        
        Args:
            inline_image: Base64 encoded image dengan prefix data:image/jpeg;base64,
            filename: Output filename
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Extract base64 data
            if ',' in inline_image:
                base64_data = inline_image.split(',')[1]
            else:
                base64_data = inline_image
            
            # Decode base64 to image
            image_data = base64.b64decode(base64_data)
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"✓ Captcha image saved to: {filename}")
            return True
                
        except Exception as e:
            print(f"✗ Error saving captcha image: {e}")
            return False
    
    def check_bpjs(self, nik, tgl_lahir, captcha_uuid, captcha_answer):
        """
        Cek data BPJS
        
        Args:
            nik: Nomor Induk Kependudukan
            tgl_lahir: Tanggal lahir format YYYY-MM-DD
            captcha_uuid: UUID dari captcha
            captcha_answer: Jawaban captcha
            
        Returns:
            dict: Data BPJS atau None jika gagal
        """
        try:
            url = f"{self.base_url}/bpjs/detail"
            params = {
                'nik': nik,
                'tgl_lahir': tgl_lahir,
                'captcha_uuid': captcha_uuid,
                'captcha_answer': captcha_answer
            }
            
            print(f"  Checking BPJS...")
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✓ BPJS data retrieved successfully")
                    return data.get('data')
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"✗ API returned error: {error_msg}")
                    return None
            else:
                print(f"✗ HTTP Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error checking BPJS: {e}")
            return None
    
    def check_bpjs_interactive(self, nik, tgl_lahir):
        """
        Cek BPJS dengan input captcha manual
        
        Args:
            nik: Nomor Induk Kependudukan
            tgl_lahir: Tanggal lahir format YYYY-MM-DD
            
        Returns:
            dict: Data BPJS atau None jika gagal
        """
        print(f"\n{'='*60}")
        print(f"Checking NIK: {nik} | DOB: {tgl_lahir}")
        print(f"{'='*60}")
        
        max_attempts = 5
        for attempt in range(max_attempts):
            print(f"\nAttempt {attempt + 1}/{max_attempts}")
            
            # Generate captcha
            captcha_uuid, inline_image = self.generate_captcha()
            if not captcha_uuid or not inline_image:
                print("  Retrying in 2 seconds...")
                time.sleep(2)
                continue
            
            # Save captcha image
            captcha_filename = f'captcha_{attempt+1}.jpg'
            self.save_captcha_image(inline_image, captcha_filename)
            
            # Ask user to input captcha
            print(f"\n📷 Please open the captcha image: {captcha_filename}")
            captcha_answer = input("Enter captcha text (or 'q' to quit): ").strip()
            
            if captcha_answer.lower() == 'q':
                print("Cancelled by user")
                return None
            
            if not captcha_answer:
                print("Empty captcha answer, retrying...")
                continue
            
            print(f"Using captcha answer: {captcha_answer}")
            
            # Check BPJS
            result = self.check_bpjs(nik, tgl_lahir, captcha_uuid, captcha_answer)
            if result:
                return result
            
            print("  Retrying in 2 seconds...")
            time.sleep(2)
        
        print(f"\n✗ Failed after {max_attempts} attempts")
        return None
    
    def format_result(self, nik, tgl_lahir, data):
        """
        Format hasil untuk display
        
        Args:
            nik: NIK yang dicek
            tgl_lahir: Tanggal lahir
            data: Data dari API
            
        Returns:
            dict: Formatted result
        """
        if not data:
            return {
                'nik': nik,
                'tgl_lahir': tgl_lahir,
                'status': 'FAILED',
                'timestamp': datetime.now().isoformat()
            }
        
        response = data.get('response', {})
        return {
            'nik': nik,
            'tgl_lahir': tgl_lahir,
            'status': 'SUCCESS',
            'nama_peserta': response.get('namapeserta', 'N/A'),
            'status_peserta': response.get('nmstatuspeserta', 'N/A'),
            'jenis_peserta': response.get('nmjenispeserta', 'N/A'),
            'faskes_terdaftar': response.get('faskesterdaftar', 'N/A'),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results, filename='bpjs_results.json'):
        """
        Simpan hasil ke file JSON
        
        Args:
            results: List of results
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Results saved to {filename}")
        except Exception as e:
            print(f"\n✗ Error saving results: {e}")


def main():
    """
    Main function - contoh penggunaan
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           BPJS CHECKER - MANUAL CAPTCHA INPUT                ║
║           No OCR Required - User Input Captcha               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Bearer token dari file atau hardcode
    BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlOWNlYmViMS01Mzc0LTRiOGMtYmVkOS1kZGYxMGMzZjdhZDciLCJzdWIiOiJkaXJ1NzY4QGdtYWlsLmNvbSIsInJlZnJlc2hfdG9rZW4iOiI1NzYxZDlkYy1lMjM1LTRlYjUtYWE0My0xMWRiZWU0ZjJjZGIiLCJleHAiOjE3NzI1NzAxMzAsInJlZmVzaF90b2tlbl9leHAiOjE3ODI5MzgxMzAsInNjb3BlIjoiYWN0aXZpdHkudXNlciBkaXNjdXNzaW9uLmNyZWF0ZSBkaXNjdXNzaW9uLnJlYWN0IHN0b3J5LnJlYWN0IHJlcG9ydC5jcmVhdGUifQ.XcZqW7XMNJ4z7_cdtLz3BGDOhvPD7JRgHtq6ZCKzu_0"
    
    # Inisialisasi checker
    checker = BPJSCheckerManual(BEARER_TOKEN)
    
    # Data NIK yang akan dicek
    data_to_check = [
        {'nik': '3317110608050001', 'tgl_lahir': '2005-08-06'},
        # Tambahkan NIK lain di sini
    ]
    
    # Proses semua data
    results = []
    for idx, data in enumerate(data_to_check, 1):
        print(f"\n\n[{idx}/{len(data_to_check)}] Processing...")
        
        nik = data['nik']
        tgl_lahir = data['tgl_lahir']
        
        # Check BPJS dengan manual captcha input
        bpjs_data = checker.check_bpjs_interactive(nik, tgl_lahir)
        
        # Format dan simpan hasil
        result = checker.format_result(nik, tgl_lahir, bpjs_data)
        results.append(result)
        
        # Display hasil
        print(f"\n{'─'*60}")
        print(f"RESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'─'*60}")
        
        # Delay antar request
        if idx < len(data_to_check):
            print("\nWaiting 3 seconds before next request...")
            time.sleep(3)
    
    # Simpan semua hasil
    checker.save_results(results)
    
    # Summary
    print(f"\n\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total processed: {len(results)}")
    print(f"Success: {sum(1 for r in results if r['status'] == 'SUCCESS')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'FAILED')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
