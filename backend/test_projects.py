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

def test_projects():
    """Test project management endpoints"""
    
    print("=" * 60)
    print("TESTING PROJECT MANAGEMENT API")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get all projects
    print("\n1. Testing Get All Projects...")
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        projects = response.json()['data']
        print(f"   ✅ Retrieved {len(projects)} projects")
        if projects:
            print(f"      First project: {projects[0]['title']} ({projects[0]['code']})")
    else:
        print("   ❌ Failed to get projects!")
        return
    
    # Test 2: Create new project
    print("\n2. Testing Create Project...")
    new_project = {
        "title": "AI Chatbot Development",
        "description": "Build an AI-powered customer service chatbot",
        "status": "planning",
        "priority": "high",
        "start_date": "2024-12-01",
        "end_date": "2025-03-31",
        "budget": 75000.0,
        "estimated_hours": 600,
        "manager_id": 2
    }
    
    response = requests.post(f"{BASE_URL}/projects/", json=new_project, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        project_data = response.json()['data']['project']
        new_project_id = project_data['id']
        print(f"   ✅ Project created!")
        print(f"      ID: {new_project_id}")
        print(f"      Code: {project_data['code']}")
        print(f"      Title: {project_data['title']}")
    else:
        print("   ❌ Failed to create project!")
        print(f"   Response: {response.json()}")
        return
    
    # Test 3: Get specific project
    print("\n3. Testing Get Project by ID...")
    response = requests.get(f"{BASE_URL}/projects/{new_project_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        project = response.json()['data']['project']
        print(f"   ✅ Project retrieved!")
        print(f"      Title: {project['title']}")
        print(f"      Status: {project['status']}")
        print(f"      Priority: {project['priority']}")
        print(f"      Completion: {project['completion_percentage']}%")
    else:
        print("   ❌ Failed to get project!")
    
    # Test 4: Update project
    print("\n4. Testing Update Project...")
    update_data = {
        "status": "in_progress",
        "priority": "critical",
        "description": "Updated: Build an advanced AI chatbot with NLP capabilities"
    }
    
    response = requests.put(f"{BASE_URL}/projects/{new_project_id}", json=update_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        updated_project = response.json()['data']['project']
        print(f"   ✅ Project updated!")
        print(f"      New Status: {updated_project['status']}")
        print(f"      New Priority: {updated_project['priority']}")
    else:
        print("   ❌ Failed to update project!")
    
    # Test 5: Get project stats
    print("\n5. Testing Get Project Stats...")
    response = requests.get(f"{BASE_URL}/projects/1/stats", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()['data']
        print(f"   ✅ Stats retrieved!")
        print(f"      Total Tasks: {stats['tasks']['total']}")
        print(f"      Completed: {stats['tasks']['completed']}")
        print(f"      In Progress: {stats['tasks']['in_progress']}")
        print(f"      Team Size: {stats['team']['size']}")
        print(f"      Estimated Hours: {stats['hours']['estimated']}")
        print(f"      Actual Hours: {stats['hours']['actual']}")
    else:
        print("   ❌ Failed to get stats!")
    
    # Test 6: Filter projects
    print("\n6. Testing Filter Projects by Status...")
    response = requests.get(f"{BASE_URL}/projects/?status=in_progress", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        filtered = response.json()['data']
        print(f"   ✅ Retrieved {len(filtered)} in-progress projects")
    else:
        print("   ❌ Failed to filter projects!")
    
    # Test 7: Search projects
    print("\n7. Testing Search Projects...")
    response = requests.get(f"{BASE_URL}/projects/?search=commerce", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        search_results = response.json()['data']
        print(f"   ✅ Found {len(search_results)} projects matching 'commerce'")
        if search_results:
            print(f"      Result: {search_results[0]['title']}")
    else:
        print("   ❌ Failed to search projects!")
    
    # Test 8: Get dashboard
    print("\n8. Testing Dashboard...")
    response = requests.get(f"{BASE_URL}/projects/dashboard", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        dashboard = response.json()['data']
        print(f"   ✅ Dashboard retrieved!")
        print(f"      Total Projects: {dashboard['summary']['total_projects']}")
        print(f"      Active: {dashboard['summary']['active_projects']}")
        print(f"      Completed: {dashboard['summary']['completed_projects']}")
        print(f"      Overdue: {dashboard['summary']['overdue_projects']}")
    else:
        print("   ❌ Failed to get dashboard!")
    
    # Test 9: Archive project
    print("\n9. Testing Archive Project...")
    response = requests.put(f"{BASE_URL}/projects/{new_project_id}/archive", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Project archived!")
    else:
        print("   ❌ Failed to archive project!")
    
    # Test 10: Filter by manager
    print("\n10. Testing Filter by Manager...")
    response = requests.get(f"{BASE_URL}/projects/?manager_id=2", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        manager_projects = response.json()['data']
        print(f"   ✅ Retrieved {len(manager_projects)} projects for manager")
    else:
        print("   ❌ Failed to filter by manager!")
    
    # Test 11: Pagination
    print("\n11. Testing Pagination...")
    response = requests.get(f"{BASE_URL}/projects/?page=1&per_page=2", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Pagination works!")
        print(f"      Page: {result['pagination']['page']}")
        print(f"      Per Page: {result['pagination']['per_page']}")
        print(f"      Total: {result['pagination']['total']}")
        print(f"      Pages: {result['pagination']['pages']}")
    else:
        print("   ❌ Pagination failed!")
    
    print("\n" + "=" * 60)
    print("✅ ALL PROJECT TESTS COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_projects()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")