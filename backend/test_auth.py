import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_auth_flow():
    """Test complete authentication flow"""
    
    print("=" * 60)
    print("TESTING AUTHENTICATION API")
    print("=" * 60)
    
    # Test 1: Register new user
    print("\n1. Testing Registration...")
    register_data = {
        "email": "test.user@company.com",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "role": "employee",
        "skills": ["Python", "Testing"],
        "weekly_capacity": 40
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("   ✅ Registration successful!")
        new_user_token = response.json()['data']['access_token']
    else:
        print("   ❌ Registration failed!")
        return
    
    # Test 2: Login with existing user
    print("\n2. Testing Login...")
    login_data = {
        "email": "admin@company.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Login successful!")
        admin_token = response.json()['data']['access_token']
        print(f"   Token: {admin_token[:50]}...")
    else:
        print("   ❌ Login failed!")
        print(f"   Response: {response.json()}")
        return
    
    # Test 3: Get current user profile
    print("\n3. Testing Get Current User...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()['data']['user']
        print("   ✅ Profile retrieved!")
        print(f"   User: {user_data['full_name']} ({user_data['role']})")
    else:
        print("   ❌ Failed to get profile!")
    
    # Test 4: Get all users (with admin token)
    print("\n4. Testing Get All Users...")
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()['data']
        print(f"   ✅ Retrieved {len(users)} users")
        for user in users[:3]:  # Show first 3
            print(f"      - {user['full_name']} ({user['email']}) - {user['role']}")
    else:
        print("   ❌ Failed to get users!")
    
    # Test 5: Get specific user
    print("\n5. Testing Get User by ID...")
    response = requests.get(f"{BASE_URL}/users/1", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user = response.json()['data']['user']
        print(f"   ✅ User retrieved: {user['full_name']}")
    else:
        print("   ❌ Failed to get user!")
    
    # Test 6: Get user workload
    print("\n6. Testing Get User Workload...")
    response = requests.get(f"{BASE_URL}/users/4/workload", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        workload = response.json()['data']
        print(f"   ✅ Workload retrieved!")
        print(f"      User: {workload['user_name']}")
        print(f"      Capacity: {workload['weekly_capacity']}h")
        print(f"      Current Load: {workload['current_workload']}h")
        print(f"      Available: {workload['available_capacity']}h")
        print(f"      Utilization: {workload['utilization_percentage']}%")
        print(f"      Overloaded: {workload['is_overloaded']}")
    else:
        print("   ❌ Failed to get workload!")
    
    # Test 7: Change password
    print("\n7. Testing Change Password...")
    change_pw_data = {
        "current_password": "admin123",
        "new_password": "NewAdmin123"
    }
    response = requests.put(f"{BASE_URL}/auth/change-password", json=change_pw_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Password changed!")
        
        # Change it back
        change_back_data = {
            "current_password": "NewAdmin123",
            "new_password": "admin123"
        }
        requests.put(f"{BASE_URL}/auth/change-password", json=change_back_data, headers=headers)
        print("   ✅ Password restored to original")
    else:
        print("   ❌ Failed to change password!")
    
    # Test 8: Test invalid login
    print("\n8. Testing Invalid Login...")
    invalid_login = {
        "email": "admin@company.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print("   ✅ Invalid login correctly rejected!")
    else:
        print("   ❌ Security issue: invalid login accepted!")
    
    # Test 9: Test accessing protected route without token
    print("\n9. Testing Protected Route Without Token...")
    response = requests.get(f"{BASE_URL}/users/")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print("   ✅ Unauthorized access correctly blocked!")
    else:
        print("   ❌ Security issue: unauthorized access allowed!")
    
    # Test 10: Filter users by role
    print("\n10. Testing User Filtering...")
    response = requests.get(f"{BASE_URL}/users/?role=employee", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        employees = response.json()['data']
        print(f"   ✅ Retrieved {len(employees)} employees")
    else:
        print("   ❌ Failed to filter users!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")