#!/usr/bin/env python3
"""
BPJS Checker - Batch Processing dari CSV
Membaca data dari CSV dan proses secara otomatis
"""

import csv
import json
import sys
from bpjs_checker import BPJSChecker
import time


def read_csv_data(filename):
    """
    Baca data NIK dari file CSV
    
    Format CSV:
    nik,tgl_lahir
    3317110608050001,2005-08-06
    1234567890123456,1990-01-01
    
    Args:
        filename: Path ke file CSV
        
    Returns:
        list: List of dict dengan nik dan tgl_lahir
    """
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'nik' in row and 'tgl_lahir' in row:
                    data.append({
                        'nik': row['nik'].strip(),
                        'tgl_lahir': row['tgl_lahir'].strip()
                    })
        print(f"✓ Loaded {len(data)} records from {filename}")
        return data
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return []
    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        return []


def create_sample_csv(filename='input_nik.csv'):
    """
    Buat sample CSV file
    
    Args:
        filename: Output filename
    """
    sample_data = [
        {'nik': '3317110608050001', 'tgl_lahir': '2005-08-06'},
        {'nik': '1234567890123456', 'tgl_lahir': '1990-01-01'},
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['nik', 'tgl_lahir'])
            writer.writeheader()
            writer.writerows(sample_data)
        print(f"✓ Sample CSV created: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error creating sample CSV: {e}")
        return False


def save_to_csv(results, filename='bpjs_results.csv'):
    """
    Simpan hasil ke CSV
    
    Args:
        results: List of results
        filename: Output filename
    """
    if not results:
        print("No results to save")
        return
    
    try:
        fieldnames = list(results[0].keys())
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"✓ Results saved to {filename}")
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")


def main():
    """
    Main function untuk batch processing
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║        BPJS CHECKER - BATCH PROCESSING                       ║
║        Process multiple NIK from CSV file                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <input_csv> [bearer_token]")
        print(f"\nOr create sample CSV:")
        print(f"  {sys.argv[0]} --create-sample")
        print(f"\nExample:")
        print(f"  {sys.argv[0]} input_nik.csv")
        print(f"  {sys.argv[0]} input_nik.csv YOUR_BEARER_TOKEN")
        
        # Offer to create sample
        response = input("\nCreate sample CSV? (y/n): ").strip().lower()
        if response == 'y':
            create_sample_csv()
        return
    
    # Create sample mode
    if sys.argv[1] == '--create-sample':
        create_sample_csv()
        return
    
    # Read input CSV
    input_file = sys.argv[1]
    data_to_check = read_csv_data(input_file)
    
    if not data_to_check:
        print("No data to process")
        return
    
    # Bearer token
    if len(sys.argv) >= 3:
        bearer_token = sys.argv[2]
    else:
        # Default token dari capture
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlOWNlYmViMS01Mzc0LTRiOGMtYmVkOS1kZGYxMGMzZjdhZDciLCJzdWIiOiJkaXJ1NzY4QGdtYWlsLmNvbSIsInJlZnJlc2hfdG9rZW4iOiI1NzYxZDlkYy1lMjM1LTRlYjUtYWE0My0xMWRiZWU0ZjJjZGIiLCJleHAiOjE3NzI1NzAxMzAsInJlZmVzaF90b2tlbl9leHAiOjE3ODI5MzgxMzAsInNjb3BlIjoiYWN0aXZpdHkudXNlciBkaXNjdXNzaW9uLmNyZWF0ZSBkaXNjdXNzaW9uLnJlYWN0IHN0b3J5LnJlYWN0IHJlcG9ydC5jcmVhdGUifQ.XcZqW7XMNJ4z7_cdtLz3BGDOhvPD7JRgHtq6ZCKzu_0"
        print("⚠ Using default bearer token from capture")
    
    # Initialize checker
    checker = BPJSChecker(bearer_token)
    
    # Process all data
    results = []
    success_count = 0
    failed_count = 0
    
    print(f"\nProcessing {len(data_to_check)} records...\n")
    
    for idx, data in enumerate(data_to_check, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(data_to_check)}] Processing...")
        print(f"{'='*70}")
        
        nik = data['nik']
        tgl_lahir = data['tgl_lahir']
        
        # Check BPJS dengan auto captcha solving
        bpjs_data = checker.check_bpjs_auto(nik, tgl_lahir, max_captcha_attempts=5)
        
        # Format dan simpan hasil
        result = checker.format_result(nik, tgl_lahir, bpjs_data)
        results.append(result)
        
        if result['status'] == 'SUCCESS':
            success_count += 1
        else:
            failed_count += 1
        
        # Display hasil
        print(f"\n{'─'*70}")
        print(f"RESULT #{idx}:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'─'*70}")
        
        # Delay antar request
        if idx < len(data_to_check):
            delay = 3
            print(f"\nWaiting {delay} seconds before next request...")
            time.sleep(delay)
    
    # Simpan hasil
    print(f"\n\nSaving results...")
    checker.save_results(results, 'bpjs_results.json')
    save_to_csv(results, 'bpjs_results.csv')
    
    # Summary
    print(f"\n\n{'='*70}")
    print(f"FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Total processed: {len(results)}")
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Success rate: {(success_count/len(results)*100):.1f}%")
    print(f"{'='*70}\n")
    
    # Show success results
    if success_count > 0:
        print("\nSuccessful Results:")
        print(f"{'─'*70}")
        for result in results:
            if result['status'] == 'SUCCESS':
                print(f"NIK: {result['nik']}")
                print(f"  Nama: {result['nama_peserta']}")
                print(f"  Status: {result['status_peserta']}")
                print(f"  Jenis: {result['jenis_peserta']}")
                print(f"  Faskes: {result['faskes_terdaftar']}")
                print()


if __name__ == "__main__":
    main()
