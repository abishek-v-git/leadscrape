from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactSearchForm
from .tasks import search_contacts_sync

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
from dotenv import load_dotenv
import pandas as pd  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart 

# @csrf_exempt
# @require_http_methods(["POST"])
# def dummy_email_test(request):
#     """Dummy email test endpoint - sends to hardcoded test list"""
#     print("📧 DUMMY EMAIL TEST TRIGGERED")
    
#     try:
#         test_recipients = [
#             "abishekabido@gmail.com",  
#         ]
        
#         smtp_host = os.getenv("SMTP_HOST")
#         smtp_port = int(os.getenv("SMTP_PORT", 587))
#         smtp_user = os.getenv("SMTP_USER")
#         smtp_pass = os.getenv("SMTP_PASS")
        
#         if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
#             raise ValueError("SMTP credentials missing from .env")
        
#         sent_count = 0
#         for recipient in test_recipients:
#             # ✅ FIXED: Uppercase MIME classes
#             msg = MIMEMultipart()
#             msg['From'] = smtp_user
#             msg['To'] = recipient
#             msg['Subject'] = "🚀 TEST Cold Email - Contact Search Lead"
            
#             body = f"""
#             Hi there,
            
#             This is a **DUMMY TEST EMAIL** from your Contact Search app!
            
#             🎉 Your search functionality is working perfectly!
#             📧 This proves SMTP is configured correctly.
            
#             Test recipient: {recipient}
#             Sent at: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}
            
#             No action needed - this is just a test!
            
#             Best,
#             Your AI Search Assistant
#             """
            
#             msg.attach(MIMEText(body, 'plain'))  # ✅ FIXED
            
#             server = smtplib.SMTP(smtp_host, smtp_port)
#             server.starttls()
#             server.login(smtp_user, smtp_pass)
#             text = msg.as_string()
#             server.sendmail(smtp_user, recipient, text)
#             server.quit()
            
#             sent_count += 1
#             print(f"✅ Dummy email sent to: {recipient}")
        
#         print(f"🎉 Dummy test completed! {sent_count} emails sent")
#         return JsonResponse({
#             'status': 'success', 
#             'message': f'Dummy emails sent to {sent_count} test recipients'
#         })
        
#     except Exception as e:
#         print(f"❌ Dummy email failed: {str(e)}")
#         return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def dummy_email_test(request):
    """Dummy email test - sends personalized cold emails to test list"""
    print("📧 DUMMY COLD EMAIL TEST TRIGGERED")
    
    try:
        # Dummy test recipients WITH sample lead data
        test_leads = [
            {
                "email": "abishekabido@gmail.com",
                "first_name": "Abishek", 
                "last_name": "V", 
                "company": "INESS Global Solutions Test",
                "title": "Supply Chain Manager"
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
Your Name  
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



