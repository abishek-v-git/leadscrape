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
