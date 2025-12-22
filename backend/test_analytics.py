import requests
import json

BASE_URL = 'http://localhost:5000/api'

def get_auth_token():
    """Login and get auth token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@company.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()['data']['access_token']
    return None

def test_analytics():
    """Test analytics and bulk operations"""
    
    print("=" * 60)
    print("TESTING ANALYTICS & BULK OPERATIONS")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Overview Analytics
    print("\n1. Testing Overview Analytics...")
    response = requests.get(f"{BASE_URL}/analytics/overview", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Overview retrieved!")
        print(f"      Total Users: {data['users']['total']}")
        print(f"      Total Projects: {data['projects']['total']}")
        print(f"      Active Projects: {data['projects']['active']}")
        print(f"      Total Tasks: {data['tasks']['total']}")
        print(f"      Completed Tasks: {data['tasks']['completed']}")
        print(f"      Team Utilization: {data['team']['utilization_rate']}%")
    else:
        print("   ❌ Failed to get overview!")
    
    # Test 2: Projects by Status
    print("\n2. Testing Projects by Status...")
    response = requests.get(f"{BASE_URL}/analytics/projects-by-status", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['data']
        print(f"   ✅ Status distribution retrieved!")
        for item in data:
            print(f"      {item['status']}: {item['count']} projects")
    else:
        print("   ❌ Failed!")
    
    # Test 3: Projects by Priority
    print("\n3. Testing Projects by Priority...")
    response = requests.get(f"{BASE_URL}/analytics/projects-by-priority", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['data']
        print(f"   ✅ Priority distribution retrieved!")
        for item in data:
            print(f"      {item['priority']}: {item['count']} projects")
    else:
        print("   ❌ Failed!")
    
    # Test 4: Team Workload
    print("\n4. Testing Team Workload...")
    response = requests.get(f"{BASE_URL}/analytics/team-workload", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Team workload retrieved!")
        print(f"      Total Members: {data['summary']['total_members']}")
        print(f"      Overloaded: {data['summary']['overloaded']}")
        print(f"      Available: {data['summary']['available']}")
        
        print(f"\n      Top 3 Team Members:")
        for member in data['team_members'][:3]:
            print(f"         {member['name']}: {member['utilization_percentage']}% ({member['status']})")
    else:
        print("   ❌ Failed!")
    
    # Test 5: Tasks by Status
    print("\n5. Testing Tasks by Status...")
    response = requests.get(f"{BASE_URL}/analytics/tasks-by-status", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['data']
        print(f"   ✅ Task status distribution retrieved!")
        for item in data:
            print(f"      {item['status']}: {item['count']} tasks")
    else:
        print("   ❌ Failed!")
    
    # Test 6: Upcoming Deadlines
    print("\n6. Testing Upcoming Deadlines...")
    response = requests.get(f"{BASE_URL}/analytics/upcoming-deadlines?days=30", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Upcoming deadlines retrieved!")
        print(f"      Critical (0-2 days): {len(data['critical'])}")
        print(f"      Warning (3-5 days): {len(data['warning'])}")
        print(f"      Upcoming (6+ days): {len(data['upcoming'])}")
    else:
        print("   ❌ Failed!")
    
    # Test 7: Productivity Trends
    print("\n7. Testing Productivity Trends...")
    response = requests.get(f"{BASE_URL}/analytics/productivity-trends?days=7", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Productivity trends retrieved!")
        print(f"      Total Completed: {data['summary']['total_completed']}")
        print(f"      Avg Per Day: {data['summary']['average_per_day']}")
    else:
        print("   ❌ Failed!")
    
    # Test 8: Top Performers
    print("\n8. Testing Top Performers...")
    response = requests.get(f"{BASE_URL}/analytics/top-performers?limit=3", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['performers']
        print(f"   ✅ Top performers retrieved!")
        for i, performer in enumerate(data, 1):
            print(f"      {i}. {performer['name']}: {performer['completed_tasks']} tasks")
    else:
        print("   ❌ Failed!")
    
    # Test 9: Activity Feed
    print("\n9. Testing Activity Feed...")
    response = requests.get(f"{BASE_URL}/analytics/activity-feed?limit=5", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['activities']
        print(f"   ✅ Activity feed retrieved!")
        print(f"      Recent activities: {len(data)}")
        for activity in data[:3]:
            print(f"         - {activity['type']} at {activity['timestamp']}")
    else:
        print("   ❌ Failed!")
    
    # Test 10: Bulk Update Task Status
    print("\n10. Testing Bulk Update Task Status...")
    bulk_data = {
        "task_ids": [1, 2],
        "status": "in_progress"
    }
    response = requests.put(f"{BASE_URL}/bulk/tasks/update-status", json=bulk_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Bulk status update successful!")
        print(f"      Updated: {data['updated']} tasks")
    else:
        print("   ❌ Failed!")
    
    # Test 11: Bulk Update Task Priority
    print("\n11. Testing Bulk Update Task Priority...")
    bulk_data = {
        "task_ids": [1, 2, 3],
        "priority": "critical"
    }
    response = requests.put(f"{BASE_URL}/bulk/tasks/update-priority", json=bulk_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Bulk priority update successful!")
        print(f"      Updated: {data['updated']} tasks")
    else:
        print("   ❌ Failed!")
    
    # Test 12: Bulk Assign Tasks
    print("\n12. Testing Bulk Assign Tasks...")
    bulk_data = {
        "task_ids": [3, 4],
        "user_id": 6,
        "assigned_hours_per_task": 5
    }
    response = requests.post(f"{BASE_URL}/bulk/tasks/assign", json=bulk_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   ✅ Bulk assignment successful!")
        print(f"      Assigned: {data['assigned']} tasks")
    else:
        print(f"   ⚠️  Bulk assignment response: {response.json()['message']}")
    
    # Test 13: Project Completion Forecast
    print("\n13. Testing Project Completion Forecast...")
    response = requests.get(f"{BASE_URL}/analytics/project-completion-forecast", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']['projects']
        print(f"   ✅ Forecast retrieved!")
        print(f"      Projects analyzed: {len(data)}")
        if data:
            for proj in data[:2]:
                print(f"         {proj['project']['title']}: {proj['forecast']['days_remaining']} days remaining")
    else:
        print("   ❌ Failed!")
    
    print("\n" + "=" * 60)
    print("✅ ALL ANALYTICS & BULK TESTS COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_analytics()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")