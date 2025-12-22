import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_create_user():
    print("1. Logging in as Admin...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@company.com",
            "password": "Admin@123"
        })
        
        if resp.status_code != 200:
            print(f"[FAIL] Login failed: {resp.status_code} - {resp.text}")
            return
            
        token = resp.json()['data']['access_token']
        print("   [OK] Login successful.")
        
        print("\n2. Creating User...")
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "email": "testuser@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "manager",
            "skills": "python",
            "weekly_capacity": 40,
            "temp_password": "Welcome@123"
        }
        
        resp = requests.post(f"{BASE_URL}/users/", json=payload, headers=headers)
        
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to server. Is it running on port 5000?")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    test_create_user()
