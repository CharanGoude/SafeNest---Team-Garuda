"""
SafeNest v2.0 — Transaction Simulator
Simulates real transactions from mobile banking to test the fraud detection pipeline
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_KEY = "sk-safenest-demo-key-2026"

MERCHANTS = [
    {"name": "Amazon", "mcc": "5411", "risk": "LOW"},
    {"name": "Starbucks", "mcc": "5812", "risk": "LOW"},
    {"name": "Best Buy", "mcc": "5731", "risk": "LOW"},
    {"name": "Unknown Merchant XYZ", "mcc": "9999", "risk": "HIGH"},
    {"name": "Casino Las Vegas", "mcc": "7011", "risk": "MEDIUM"},
    {"name": "Forex Exchange", "mcc": "6211", "risk": "HIGH"},
]

LOCATIONS = [
    {"city": "San Francisco", "country": "US", "risk": "LOW"},
    {"city": "New York", "country": "US", "risk": "LOW"},
    {"city": "Bangkok", "country": "TH", "risk": "MEDIUM"},
    {"city": "Moscow", "country": "RU", "risk": "HIGH"},
    {"city": "Lagos", "country": "NG", "risk": "HIGH"},
]

class TransactionSimulator:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.transaction_counter = 0

    def generate_transaction(self, **overrides) -> Dict[str, Any]:
        """Generate a realistic transaction"""
        self.transaction_counter += 1
        
        merchant = random.choice(MERCHANTS)
        location = random.choice(LOCATIONS)
        
        transaction = {
            "transaction_id": f"TX_SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.transaction_counter:05d}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "account_number": f"****{random.randint(1000, 9999)}",
            "user_id": f"USER_{random.randint(10000, 99999)}",
            "amount": round(random.uniform(500, 415000), 2),
            "currency": "INR",
            "transaction_type": "PAYMENT",
            "merchant_name": merchant["name"],
            "merchant_mcc": merchant["mcc"],
            "location_country": location["country"],
            "location_city": location["city"],
            "device_id": f"device_{random.randint(100000, 999999)}",
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "is_new_device": random.choice([True, False]),
            "account_age_days": random.randint(30, 3650),
            "user_avg_transaction": round(random.uniform(100, 2000), 2),
            "transaction_count_24h": random.randint(1, 10),
            "transaction_amount_24h": round(random.uniform(100, 10000), 2),
            "is_international": location["country"] != "US",
            "browser_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
        }
        
        # Apply overrides
        transaction.update(overrides)
        return transaction

    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Send transaction to SafeNest for analysis"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                headers=self.headers,
                json=transaction,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def simulate_normal_transaction(self):
        """Simulate a normal, low-risk transaction"""
        print("\n" + "="*70)
        print("📱 SIMULATING: Normal Transaction")
        print("="*70)
        
        tx = self.generate_transaction(
            amount=5000.00,
            merchant_name="Starbucks",
            location_city="Mumbai",
            location_country="IN",
            is_new_device=False,
            account_age_days=500
        )
        
        print(f"\n📤 Sending to SafeNest: {tx['merchant_name']} - ₹{tx['amount']}")
        result = self.analyze_transaction(tx)
        
        print(f"\n✅ Response from SafeNest:")
        print(json.dumps(result, indent=2))
        return result

    def simulate_high_risk_transaction(self):
        """Simulate a high-risk transaction requiring OTP"""
        print("\n" + "="*70)
        print("⚠️  SIMULATING: High-Risk Transaction (Requires OTP)")
        print("="*70)
        
        tx = self.generate_transaction(
            amount=415000.00,
            merchant_name="Forex Exchange",
            location_city="Mumbai",
            location_country="IN",
            is_new_device=True,
            is_international=True,
            account_age_days=30
        )
        
        print(f"\n📤 Sending to SafeNest: {tx['merchant_name']} - ₹{tx['amount']}")
        result = self.analyze_transaction(tx)
        
        print(f"\n⚠️  Response from SafeNest:")
        print(json.dumps(result, indent=2))
        return result

    def simulate_fraud_transaction(self):
        """Simulate a fraudulent transaction"""
        print("\n" + "="*70)
        print("🚨 SIMULATING: Fraudulent Transaction (Should be BLOCKED)")
        print("="*70)
        
        tx = self.generate_transaction(
            amount=830000.00,
            merchant_name="Unknown Merchant XYZ",
            location_city="Lagos",
            location_country="NG",
            is_new_device=True,
            is_international=True,
            account_age_days=10,
            transaction_count_24h=20,
            transaction_amount_24h=4145000.00
        )
        
        print(f"\n📤 Sending to SafeNest: {tx['merchant_name']} - ₹{tx['amount']}")
        result = self.analyze_transaction(tx)
        
        print(f"\n🚨 Response from SafeNest:")
        print(json.dumps(result, indent=2))
        return result

    def simulate_continuous_transactions(self, count: int = 10, interval: float = 2.0):
        """Simulate continuous transaction stream (like real traffic)"""
        print("\n" + "="*70)
        print(f"🔄 SIMULATING: {count} Continuous Transactions")
        print(f"   Interval: {interval}s between transactions")
        print("="*70)
        
        scenarios = [
            ("normal", self.simulate_normal_transaction),
            ("normal", self.simulate_normal_transaction),
            ("normal", self.simulate_normal_transaction),
            ("risky", self.simulate_high_risk_transaction),
            ("fraud", self.simulate_fraud_transaction),
        ]
        
        results = []
        for i in range(count):
            scenario_type, scenario_func = random.choice(scenarios)
            print(f"\n[{i+1}/{count}] Simulating {scenario_type} transaction...")
            result = scenario_func()
            results.append(result)
            
            if i < count - 1:
                print(f"\n⏳ Waiting {interval}s before next transaction...")
                time.sleep(interval)
        
        print("\n" + "="*70)
        print(f"✅ Simulation Complete: {count} transactions processed")
        print("="*70)
        return results

    def test_api_health(self):
        """Check if SafeNest API is running"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=3
            )
            if response.status_code == 200:
                print("✅ SafeNest API is running on", self.base_url)
                return True
            else:
                print(f"❌ SafeNest API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to SafeNest API at {self.base_url}")
            print("   Make sure backend is running: python -m uvicorn main:app --reload --port 8000")
            return False

def main():
    print("\n" + "🛡️ "*20)
    print("SafeNest v2.0 — Real-Time Fraud Detection Simulator")
    print("🛡️ "*20 + "\n")
    
    simulator = TransactionSimulator(BASE_URL, API_KEY)
    
    # Check API health
    if not simulator.test_api_health():
        return
    
    print("\n" + "-"*70)
    print("Available Scenarios:")
    print("-"*70)
    print("1. Normal Transaction (Low Risk)")
    print("2. High-Risk Transaction (Requires OTP)")
    print("3. Fraudulent Transaction (Should be Blocked)")
    print("4. Continuous Stream (10 random transactions)")
    print("5. Custom Test")
    print("0. Exit")
    print("-"*70)
    
    while True:
        choice = input("\n👉 Select scenario (0-5): ").strip()
        
        if choice == "1":
            simulator.simulate_normal_transaction()
        elif choice == "2":
            simulator.simulate_high_risk_transaction()
        elif choice == "3":
            simulator.simulate_fraud_transaction()
        elif choice == "4":
            count = int(input("How many transactions? (default 10): ") or "10")
            simulator.simulate_continuous_transactions(count=count)
        elif choice == "5":
            print("\nCreate a custom transaction:")
            amount = float(input("Amount (default 500): ") or "500")
            merchant = input("Merchant name (default Amazon): ") or "Amazon"
            country = input("Country (default US): ") or "US"
            is_new_device = input("New device? (y/n, default n): ").lower() == "y"
            
            tx = simulator.generate_transaction(
                amount=amount,
                merchant_name=merchant,
                location_country=country,
                is_new_device=is_new_device
            )
            result = simulator.analyze_transaction(tx)
            print("\n📊 Result:")
            print(json.dumps(result, indent=2))
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
