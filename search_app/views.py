from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactSearchForm
from .tasks import search_contacts_sync
import requests
import os

def search_form(request):
    form = ContactSearchForm()
    return render(request, 'search/search_form.html', {'form': form})

@csrf_exempt
@require_http_methods(["POST"])
def start_search(request):
    print("🎯 Search POST received")
    
    form = ContactSearchForm(request.POST)
    if not form.is_valid():
        print("❌ Form invalid:", form.errors)
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    try:
        print("🚀 Starting synchronous search...")
        result = search_contacts_sync(form.cleaned_data)
        print("✅ Search completed successfully!")
        return JsonResponse({'status': 'success', 'data': result})
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


import smtplib
import os
import json
from collections import defaultdict
from dotenv import load_dotenv
import pandas as pd  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart 


@require_http_methods(["GET"])
def credit_usage(request):
    log_path = "media/credit_log.json"
    entries = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            try:
                entries = json.load(f)
            except Exception:
                entries = []

    # Group by date
    by_date = defaultdict(lambda: {"searches": 0, "contacts": 0, "emails": 0, "last_remaining": ""})
    for e in entries:
        d = e.get("date", "unknown")
        by_date[d]["searches"] += 1
        by_date[d]["contacts"] += e.get("contacts_fetched", 0)
        by_date[d]["emails"]   += e.get("emails_revealed", 0)
        by_date[d]["last_remaining"] = e.get("rate_limit_remaining", "")
        by_date[d]["daily_usage"]    = e.get("daily_usage", "")

    days = sorted(by_date.items(), reverse=True)
    return render(request, "search/credits.html", {
        "days": days,
        "entries": list(reversed(entries[-50:])),
    })


@require_http_methods(["GET"])
def apollo_raw_debug(request):
    """Test both Apollo endpoints and show exactly what each returns."""
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("APOLLO_API_KEY")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    payload = {
        "q_keywords": "logistics",
        "page": 1,
        "per_page": 1,
        "reveal_personal_emails": True,
        "reveal_phone_number": True,
    }

    results = {}
    for endpoint, key in [
        ("mixed_people/api_search", "people"),
        ("contacts/search",         "contacts"),
        ("people/search",           "people"),
    ]:
        resp = requests.post(
            f"https://api.apollo.io/v1/{endpoint}",
            headers=headers, json=payload,
        )
        data = resp.json()
        records = data.get(key, [])
        first = records[0] if records else {}
        results[endpoint] = {
            "status_code":      resp.status_code,
            "error":            data.get("error"),
            "keys_present":     list(first.keys()),
            "email":            first.get("email"),
            "personal_emails":  first.get("personal_emails"),
            "phone_numbers":    first.get("phone_numbers"),
            "phone_number":     first.get("phone_number"),
            "linkedin_url":     first.get("linkedin_url"),
            "last_name":        first.get("last_name"),
            "last_name_obfuscated": first.get("last_name_obfuscated"),
        }

    return JsonResponse(results, json_dumps_params={"indent": 2})


@csrf_exempt
@require_http_methods(["POST"])
def dummy_email_test(request):
    """Dummy email test - sends personalized cold emails to test list"""
    print("📧 DUMMY COLD EMAIL TEST TRIGGERED")
    
    try:
        test_leads = [
            {
                "email": "abishek@inessconsulting.com",
                "first_name": "Abishek", 
                "last_name": "V", 
                "company": "INESS Global Solutions Test",
                "title": "Supply chain"
            }
        ]
        
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            raise ValueError("SMTP credentials missing from .env")
        
        sent_count = 0
        for lead in test_leads:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = lead["email"]
            msg['Subject'] = f"Supply Chain Partnership Opportunity - {lead['company']}"
            
            body = f"""
Hi {lead['first_name']},

I hope this email finds you well. WE are  from INESS Global Solutions, and we specialize in delivering cutting-edge supply chain solutions to companies like yours.

Here's what we bring to the table:

• 🔗 Act as the **perfect bridge between supply and demand**
• 📦 End-to-end supply chain optimization  
• 🌍 Global logistics and procurement expertise
• ⚡ Real-time inventory and demand forecasting
• 💰 Cost reduction through intelligent sourcing

**Your role as {lead['title']} at {lead['company']} makes you the ideal person to explore this partnership.**

Could we schedule a quick 15-minute call next week to discuss how INESS can support your supply chain goals?

Looking forward to hearing from you!

Best regards,  
AAA V,
Business Development Manager  
**INESS Global Solutions**  
📧 your-email@inessglobalsolutions.com  
📱 +91-XXXXXXXXXX  
🌐 www.inessglobalsolutions.com
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(smtp_user, lead["email"], text)
            server.quit()
            
            sent_count += 1
            print(f"✅ Personalized cold email sent to: {lead['first_name']} {lead['last_name']} ({lead['email']})")
        
        print(f"🎉 Cold email test completed! {sent_count} personalized emails sent")
        return JsonResponse({
            'status': 'success', 
            'message': f'{sent_count} personalized cold emails sent to test leads!'
        })
        
    except Exception as e:
        print(f"❌ Cold email test failed: {str(e)}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)



