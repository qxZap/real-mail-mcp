import asyncio
import os
from dotenv import load_dotenv
from server import send_email, get_emails, get_unread_count, delete_email, search_emails, create_label, delete_label, add_label_to_email

load_dotenv()

async def run_tests():
    print("Starting tests...")
    
    # Test 1: Send email
    print("\n1. Testing send_email...")
    result = await send_email(
        to="xxxsk3t4xxx@gmail.com",
        subject="Test Email from MCP Server",
        body="This is a test email sent from the MCP email server.",
        is_html=False
    )
    print(f"Send email result: {result}")
    
    # Test 2: Get unread count
    print("\n2. Testing get_unread_count...")
    count = await get_unread_count()
    print(f"Unread count: {count}")
    
    # Test 3: Get emails
    print("\n3. Testing get_emails...")
    emails = await get_emails(limit=5)
    print(f"Retrieved {len(emails)} emails")
    if isinstance(emails, list):
        for email in emails[:2]:  # Print first 2
            print(f"  - Subject: {email.get('subject', 'N/A')}")
    
    # Test 4: Search emails (example keywords)
    print("\n4. Testing search_emails...")
    search_results = await search_emails(["test"])
    print(f"Search results: {len(search_results)} emails")
    if isinstance(search_results, list):
        for email in search_results[:2]:
            print(f"  - Subject: {email.get('subject', 'N/A')}")
    
    # Test 5: Create label
    print("\n5. Testing create_label...")
    label_result = await create_label("TestLabel")
    print(f"Create label result: {label_result}")
    
    # Test 6: Delete label
    print("\n6. Testing delete_label...")
    delete_result = await delete_label("TestLabel")
    print(f"Delete label result: {delete_result}")
    
    # Test 7: Add label to email (use first email id if available)
    print("\n7. Testing add_label_to_email...")
    if isinstance(emails, list) and emails:
        add_result = await add_label_to_email(emails[0]['id'], "TestLabel")
        print(f"Add label result: {add_result}")
    else:
        print("Skipping add_label test: no emails retrieved")
    
    # Note: Delete email test skipped to avoid accidental deletion; can be added manually if needed
    print("\nTests completed.")

if __name__ == "__main__":
    asyncio.run(run_tests())