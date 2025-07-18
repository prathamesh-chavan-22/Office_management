#!/usr/bin/env python3
"""
Test script for the Ticket Management System API
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_login(username, password):
    """Test user login and return token"""
    try:
        response = requests.post(f"{AUTH_URL}/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✓ Login successful for {username}")
            return token
        else:
            print(f"✗ Login failed for {username}: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_create_ticket(token):
    """Test creating a new ticket"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with form data (simulating file upload)
        data = {
            "title": "Test Ticket - Computer Not Working",
            "description": "My computer is not starting up properly. I see a blue screen when I try to boot it. This is affecting my work productivity.",
            "priority": "high",
            "category": "IT Support"
        }
        
        response = requests.post(f"{API_URL}/tickets/", headers=headers, data=data)
        
        if response.status_code == 201:
            ticket_data = response.json()
            print(f"✓ Ticket created successfully: ID {ticket_data['id']}")
            return ticket_data['id']
        else:
            print(f"✗ Ticket creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Ticket creation error: {e}")
        return None

def test_list_tickets(token):
    """Test listing tickets"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{API_URL}/tickets/", headers=headers)
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"✓ Retrieved {len(tickets)} tickets")
            return tickets
        else:
            print(f"✗ Failed to list tickets: {response.text}")
            return []
    except Exception as e:
        print(f"✗ List tickets error: {e}")
        return []

def test_get_ticket_details(token, ticket_id):
    """Test getting ticket details"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{API_URL}/tickets/{ticket_id}/", headers=headers)
        
        if response.status_code == 200:
            ticket = response.json()
            print(f"✓ Retrieved ticket details: {ticket['title']}")
            return ticket
        else:
            print(f"✗ Failed to get ticket details: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Get ticket details error: {e}")
        return None

def test_add_comment(token, ticket_id):
    """Test adding a comment to a ticket"""
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        data = {
            "comment_text": "I have tried restarting the computer multiple times, but the issue persists. The error code on the blue screen is 0x00000124."
        }
        
        response = requests.post(f"{API_URL}/tickets/{ticket_id}/comments/", 
                               headers=headers, json=data)
        
        if response.status_code == 201:
            comment = response.json()
            print(f"✓ Comment added successfully: ID {comment['id']}")
            return comment
        else:
            print(f"✗ Failed to add comment: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Add comment error: {e}")
        return None

def test_update_ticket(token, ticket_id):
    """Test updating a ticket (admin/HR only)"""
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        data = {
            "status": "in_progress",
            "priority": "urgent"
        }
        
        response = requests.patch(f"{API_URL}/tickets/{ticket_id}/", 
                                headers=headers, json=data)
        
        if response.status_code == 200:
            ticket = response.json()
            print(f"✓ Ticket updated successfully: Status={ticket['status']}, Priority={ticket['priority']}")
            return ticket
        else:
            print(f"✗ Failed to update ticket: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Update ticket error: {e}")
        return None

def test_get_categories(token):
    """Test getting ticket categories"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{API_URL}/tickets/categories/", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✓ Retrieved {len(categories['categories'])} categories")
            print(f"   Categories: {', '.join(categories['categories'])}")
            return categories
        else:
            print(f"✗ Failed to get categories: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Get categories error: {e}")
        return None

def test_get_stats(token):
    """Test getting ticket statistics (admin/HR only)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{API_URL}/tickets/stats/", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Retrieved ticket statistics:")
            print(f"   Total tickets: {stats['total_tickets']}")
            print(f"   Open tickets: {stats['open_tickets']}")
            print(f"   In progress: {stats['in_progress_tickets']}")
            print(f"   Closed tickets: {stats['closed_tickets']}")
            return stats
        else:
            print(f"✗ Failed to get stats: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Get stats error: {e}")
        return None

def main():
    print("=== Ticket Management System API Tests ===\n")
    
    # Test with different user roles
    test_users = [
        ("admin", "admin123", "Admin User"),
        ("hr1", "hr123", "HR User"),
        ("employee1", "employee123", "Employee User")
    ]
    
    for username, password, role in test_users:
        print(f"\n--- Testing with {role} ({username}) ---")
        
        # Login
        token = test_login(username, password)
        if not token:
            continue
        
        # Get categories
        test_get_categories(token)
        
        # Create ticket
        ticket_id = test_create_ticket(token)
        if not ticket_id:
            continue
        
        # List tickets
        tickets = test_list_tickets(token)
        
        # Get ticket details
        ticket_details = test_get_ticket_details(token, ticket_id)
        
        # Add comment
        test_add_comment(token, ticket_id)
        
        # Update ticket (only admin/HR)
        if username in ["admin", "hr1"]:
            test_update_ticket(token, ticket_id)
            test_get_stats(token)
        
        # Get updated ticket details
        test_get_ticket_details(token, ticket_id)
    
    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    main()