import requests
import json

BASE_URL = 'http://localhost:5000/api'

def get_auth_token(email="admin@company.com", password="admin123"):
    """Login and get auth token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()['data']['access_token']
    return None

def test_tasks():
    """Test task management endpoints"""
    
    print("=" * 60)
    print("TESTING TASK MANAGEMENT API")
    print("=" * 60)
    
    # Get admin token
    admin_token = get_auth_token()
    if not admin_token:
        print("❌ Failed to get admin token")
        return
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Get all tasks
    print("\n1. Testing Get All Tasks...")
    response = requests.get(f"{BASE_URL}/tasks/", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        tasks = response.json()['data']
        print(f"   ✅ Retrieved {len(tasks)} tasks")
        if tasks:
            print(f"      First task: {tasks[0]['title']} ({tasks[0]['task_number']})")
    else:
        print("   ❌ Failed to get tasks!")
        return
    
    # Test 2: Create new task
    print("\n2. Testing Create Task...")
    new_task = {
        "project_id": 1,
        "title": "Implement user authentication",
        "description": "Add JWT-based authentication system",
        "status": "todo",
        "priority": "high",
        "start_date": "2024-12-01",
        "due_date": "2024-12-10",
        "estimated_hours": 16
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=new_task, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        task_data = response.json()['data']['task']
        new_task_id = task_data['id']
        print(f"   ✅ Task created!")
        print(f"      ID: {new_task_id}")
        print(f"      Number: {task_data['task_number']}")
        print(f"      Title: {task_data['title']}")
    else:
        print("   ❌ Failed to create task!")
        print(f"   Response: {response.json()}")
        return
    
    # Test 3: Get specific task
    print("\n3. Testing Get Task by ID...")
    response = requests.get(f"{BASE_URL}/tasks/{new_task_id}", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        task = response.json()['data']['task']
        print(f"   ✅ Task retrieved!")
        print(f"      Title: {task['title']}")
        print(f"      Status: {task['status']}")
        print(f"      Priority: {task['priority']}")
        print(f"      Estimated Hours: {task['estimated_hours']}")
    else:
        print("   ❌ Failed to get task!")
    
    # Test 4: Update task
    print("\n4. Testing Update Task...")
    update_data = {
        "status": "in_progress",
        "priority": "critical",
        "actual_hours": 5
    }
    
    response = requests.put(f"{BASE_URL}/tasks/{new_task_id}", json=update_data, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        updated_task = response.json()['data']['task']
        print(f"   ✅ Task updated!")
        print(f"      New Status: {updated_task['status']}")
        print(f"      Actual Hours: {updated_task['actual_hours']}")
    else:
        print("   ❌ Failed to update task!")
    
    # Test 5: Assign task to user
    print("\n5. Testing Assign Task...")
    assignment_data = {
        "user_id": 4,  # Alice
        "assigned_hours": 16,
        "notes": "Please complete by end of week"
    }
    
    response = requests.post(f"{BASE_URL}/tasks/{new_task_id}/assign", json=assignment_data, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        assignment = response.json()['data']['assignment']
        print(f"   ✅ Task assigned!")
        print(f"      Assigned to: {assignment['user']['full_name']}")
        print(f"      Hours: {assignment['assigned_hours']}")
    else:
        print("   ❌ Failed to assign task!")
        print(f"   Response: {response.json()}")
    
    # Test 6: Add comment to task
    print("\n6. Testing Add Comment...")
    comment_data = {
        "content": "Started working on the authentication module. JWT implementation in progress."
    }
    
    response = requests.post(f"{BASE_URL}/tasks/{new_task_id}/comments", json=comment_data, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        comment = response.json()['data']['comment']
        comment_id = comment['id']
        print(f"   ✅ Comment added!")
        print(f"      Comment ID: {comment_id}")
        print(f"      Content: {comment['content'][:50]}...")
    else:
        print("   ❌ Failed to add comment!")
    
    # Test 7: Filter tasks by project
    print("\n7. Testing Filter Tasks by Project...")
    response = requests.get(f"{BASE_URL}/tasks/?project_id=1", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        filtered_tasks = response.json()['data']
        print(f"   ✅ Retrieved {len(filtered_tasks)} tasks for project 1")
    else:
        print("   ❌ Failed to filter tasks!")
    
    # Test 8: Filter tasks by status
    print("\n8. Testing Filter Tasks by Status...")
    response = requests.get(f"{BASE_URL}/tasks/?status=in_progress", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        status_tasks = response.json()['data']
        print(f"   ✅ Retrieved {len(status_tasks)} in-progress tasks")
    else:
        print("   ❌ Failed to filter by status!")
    
    # Test 9: Get my tasks (as employee)
    print("\n9. Testing Get My Tasks (as Employee)...")
    employee_token = get_auth_token("alice.johnson@company.com", "employee123")
    if employee_token:
        employee_headers = {"Authorization": f"Bearer {employee_token}"}
        response = requests.get(f"{BASE_URL}/tasks/my-tasks", headers=employee_headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            my_tasks = response.json()['data']['tasks']
            print(f"   ✅ Retrieved {len(my_tasks)} assigned tasks")
            if my_tasks:
                for task in my_tasks[:3]:
                    print(f"      - {task['title']} ({task['status']})")
        else:
            print("   ❌ Failed to get my tasks!")
    else:
        print("   ⚠️  Could not test employee view (login failed)")
    
    # Test 10: Search tasks
    print("\n10. Testing Search Tasks...")
    response = requests.get(f"{BASE_URL}/tasks/?search=authentication", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        search_results = response.json()['data']
        print(f"   ✅ Found {len(search_results)} tasks matching 'authentication'")
        if search_results:
            print(f"      Result: {search_results[0]['title']}")
    else:
        print("   ❌ Failed to search tasks!")
    
    # Test 11: Update comment
    print("\n11. Testing Update Comment...")
    update_comment_data = {
        "content": "Updated: JWT authentication is now complete. Added tests."
    }
    
    response = requests.put(f"{BASE_URL}/tasks/comments/{comment_id}", json=update_comment_data, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Comment updated!")
    else:
        print("   ❌ Failed to update comment!")
    
    # Test 12: Test overload protection
    print("\n12. Testing Workload Overload Protection...")
    overload_assignment = {
        "user_id": 4,  # Alice (already has workload)
        "assigned_hours": 100,  # Way too much
        "notes": "This should fail"
    }
    
    response = requests.post(f"{BASE_URL}/tasks/1/assign", json=overload_assignment, headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        error_data = response.json()
        print(f"   ✅ Overload protection working!")
        if 'errors' in error_data:
            print(f"      Current workload: {error_data['errors'].get('current_workload')}h")
            print(f"      Available: {error_data['errors'].get('available_capacity')}h")
    else:
        print("   ⚠️  Overload protection may not be working correctly")
    
    # Test 13: Filter by assigned user
    print("\n13. Testing Filter by Assigned User...")
    response = requests.get(f"{BASE_URL}/tasks/?assigned_to=4", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user_tasks = response.json()['data']
        print(f"   ✅ Retrieved {len(user_tasks)} tasks assigned to user 4")
    else:
        print("   ❌ Failed to filter by user!")
    
    # Test 14: Unassign task
    print("\n14. Testing Unassign Task...")
    response = requests.delete(f"{BASE_URL}/tasks/{new_task_id}/unassign/4", headers=admin_headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Task unassigned!")
    else:
        print("   ❌ Failed to unassign task!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TASK TESTS COMPLETED!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_tasks()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")