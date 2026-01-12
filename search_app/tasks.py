# search_app/tasks.py
import os
import pandas as pd
import requests
import time
import uuid
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()

def search_contacts_sync(search_params):
    print("🚀 STARTING CONTACT SEARCH")
    print(f"📋 Search params: {search_params}")
    
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        print("❌ ERROR: API_KEY not found in environment")
        raise ValueError("API_KEY not found in environment")
    
    print("✅ API_KEY found")
    base_url = "https://api.apollo.io/v1"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }
    
    # Parse inputs
    keywords = [k.strip() for k in search_params['keywords'].split(',')]
    titles = [t.strip() for t in search_params['titles'].split(',')]
    location = search_params['location']
    max_results = search_params['max_results']
    per_page = search_params['per_page']
    
    print(f"🔍 Keywords: {keywords}")
    print(f"💼 Titles: {titles}")
    print(f"📍 Location: {location}")
    print(f"📊 Max results: {max_results}, Per page: {per_page}")
    
    results = []
    page = 1
    
    while len(results) < max_results:
        print(f"🌐 Fetching page {page}...")
        
        payload = {
            "q": " OR ".join(keywords),
            "person_titles": titles,
            "person_locations": [location],
            "page": page,
            "per_page": per_page
        }
        
        print(f"📤 Sending request to page {page}")
        response = requests.post(
            f"{base_url}/contacts/search",
            json=payload,
            headers=headers
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            raise ValueError(f"API request failed: {response.status_code}")
        
        data = response.json()
        contacts = data.get("contacts", [])
        print(f"📈 Found {len(contacts)} contacts on page {page}")
        
        if not contacts:
            print("✅ No more contacts found")
            break
        
        for i, c in enumerate(contacts, 1):
            org = c.get("organization", {})
            results.append({
                "Company": org.get("name", ""),
                "Company_Employees": org.get("estimated_num_employees"),
                "Company_Industry": org.get("industry", ""),
                "Company_Description": org.get("description", ""),
                "Company_Website": org.get("website_url", ""),
                "Contact_First_Name": c.get("first_name", ""),
                "Contact_Last_Name": c.get("last_name", ""),
                "Contact_Title": c.get("title", ""),
                "Contact_Email": c.get("email", ""),
                "Contact_Phone": c.get("phone_number", ""),
                "Contact_LinkedIn": c.get("linkedin_url", ""),
                "Contact_ID": c.get("id"),
                "Company_ID": org.get("id")
            })
            print(f"   Added contact {len(results)}: {c.get('first_name', '')} {c.get('last_name', '')}")
            
            if len(results) >= max_results:
                print(f"✅ Reached max results: {max_results}")
                break
        
        page += 1
        time.sleep(0.4)  # Rate limiting
    
    print(f"📊 Total results collected: {len(results)}")
    
    # Generate files WITHOUT ID columns
    file_id = str(uuid.uuid4())[:8]
    csv_path = f"media/downloads/{file_id}_contacts.csv"
    excel_path = f"media/downloads/{file_id}_contacts.xlsx"
    
    print("💾 Saving CSV file...")
    df = pd.DataFrame(results)
    
    # 👇 REMOVE THESE COLUMNS before saving
    df_clean = df.drop(columns=['Contact_ID', 'Company_ID'], errors='ignore')
    df_clean.to_csv(csv_path, index=False)
    print("✅ CSV saved (without IDs)")
    
    print("💾 Saving Excel file...")
    df_clean.to_excel(excel_path, index=False)
    print("✅ Excel saved (without IDs)")
    
    # Return preview WITHOUT IDs too
    preview_data = []
    for row in results[:10]:
        clean_row = {k: v for k, v in row.items() if k not in ['Contact_ID', 'Company_ID']}
        preview_data.append(clean_row)
    
    result = {
        'results_count': len(results),
        'csv_url': f"/media/downloads/{file_id}_contacts.csv",
        'excel_url': f"/media/downloads/{file_id}_contacts.xlsx",
        'preview_data': preview_data,
        'file_id': file_id,
        'total_rows': len(results),
        'columns': list(preview_data[0].keys()) if preview_data else []
    }
    
    print("🎉 SEARCH COMPLETED SUCCESSFULLY!")
    print(f"📁 Files generated: {file_id}_contacts.csv | {file_id}_contacts.xlsx")
    return result
