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
    print("🚀 STARTING DEEP CONTACT SEARCH")
    
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in environment")
    
    base_url = "https://api.apollo.io/v1"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }
    
    # Parse inputs with better robustness
    keywords = [k.strip() for k in search_params.get('keywords', '').split(',') if k.strip()]
    titles = [t.strip() for t in search_params.get('titles', '').split(',') if t.strip()]
    seniorities = [s.strip() for s in search_params.get('seniorities', '').split(',') if s.strip()]
    industries = [i.strip() for i in search_params.get('industries', '').split(',') if i.strip()]
    locations = [l.strip() for l in search_params.get('location', '').split(',') if l.strip()]
    company_sizes = [cs.strip() for cs in search_params.get('company_size', '').split(',') if cs.strip()]
    
    max_results = min(int(search_params.get('max_results', 50)), 500)
    per_page = min(int(search_params.get('per_page', 50)), 100)
    
    results = []
    page = 1
    
    while len(results) < max_results:
        print(f"🌐 Fetching page {page}...")
        
        payload = {
            "page": page,
            "per_page": per_page
        }
        
        # Build payload dynamically to avoid sending empty filters
        if keywords: payload["q_keywords"] = ", ".join(keywords)
        if titles: payload["person_titles"] = titles
        if seniorities: payload["person_seniorities"] = seniorities
        if industries: payload["organization_industries"] = industries
        if locations: payload["person_locations"] = locations
        if company_sizes: payload["organization_num_employees_ranges"] = company_sizes

        response = requests.post(
            f"{base_url}/contacts/search",
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            break
        
        data = response.json()
        contacts = data.get("contacts", [])
        
        if not contacts:
            break
        
        for contact in contacts:
            org = contact.get("organization", {})
            
            # Extract EVERY detail for the export
            entry = {
                # Contact Personal Details
                "First Name": contact.get("first_name"),
                "Last Name": contact.get("last_name"),
                "Job Title": contact.get("title"),
                "Seniority": contact.get("seniority"),
                "Email": contact.get("email"),
                "Direct Phone": contact.get("phone_number"),
                "LinkedIn Profile": contact.get("linkedin_url"),
                "Twitter URL": contact.get("twitter_url"),
                "Facebook URL": contact.get("facebook_url"),
                "City": contact.get("city"),
                "State": contact.get("state"),
                "Country": contact.get("country"),
                "Headline": contact.get("headline"),
                
                # Company Details
                "Company Name": org.get("name"),
                "Industry": org.get("industry"),
                "Employees": org.get("estimated_num_employees"),
                "Revenue Range": org.get("annual_revenue"),
                "Company Website": org.get("website_url"),
                "Company LinkedIn": org.get("linkedin_url"),
                "Company Twitter": org.get("twitter_url"),
                "Company Facebook": org.get("facebook_url"),
                "Company Phone": org.get("phone"),
                "Company Description": org.get("description"),
                "Company Addressing": f"{org.get('street_address', '')}, {org.get('city', '')}, {org.get('state', '')} {org.get('postal_code', '')}",
                "SEO Description": org.get("seo_description"),
                "Founded Year": org.get("founded_year")
            }
            results.append(entry)
            
            if len(results) >= max_results:
                break
        
        page += 1
        if page > data.get("pagination", {}).get("total_pages", page):
            break
        time.sleep(0.5)
    
    # Generate files
    download_dir = "media/downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    else:
        for f in os.listdir(download_dir):
            try: os.remove(os.path.join(download_dir, f))
            except: pass

    csv_path = f"{download_dir}/contacts.csv"
    excel_path = f"{download_dir}/contacts.xlsx"
    
    df = pd.DataFrame(results)
    
    # Export clean files
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)
    
    # Prepare preview (limit columns for UI)
    preview_data = []
    for row in results[:20]: # Show first 20 in UI
        preview_data.append({
            "Company": row["Company Name"],
            "Company_Industry": row["Industry"],
            "Contact_First_Name": row["First Name"],
            "Contact_Last_Name": row["Last Name"],
            "Contact_Title": row["Job Title"],
            "Contact_Email": row["Email"],
            "Contact_LinkedIn": row["LinkedIn Profile"]
        })
    
    return {
        'results_count': len(results),
        'csv_url': f"/media/downloads/contacts.csv",
        'excel_url': f"/media/downloads/contacts.xlsx",
        'preview_data': preview_data
    }
