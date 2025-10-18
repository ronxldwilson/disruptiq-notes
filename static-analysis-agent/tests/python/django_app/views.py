"""
Django views with intentional issues.
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import random

# Issue: global variable
global_counter = 0

@csrf_exempt  # Security issue: CSRF exemption
def user_profile(request):
    """User profile view with issues."""
    user_id = request.GET.get('id')

    # Security issue: SQL injection in raw query
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection!

    # Issue: unused variable
    unused_data = cursor.fetchall()

    return JsonResponse({'status': 'ok'})

def execute_shell(request):
    """Shell execution view."""
    cmd = request.POST.get('command')

    # Security issue: command injection
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return HttpResponse(result.stdout)

def generate_token(request):
    """Token generation with weak randomness."""
    # Issue: using random instead of secrets
    token = ''.join(random.choice('0123456789abcdef') for _ in range(64))
    return JsonResponse({'token': token})

def file_upload(request):
    """File upload with security issues."""
    if request.method == 'POST':
        uploaded_file = request.FILES['file']

        # Security issue: no file type validation
        with open(f'/tmp/{uploaded_file.name}', 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return JsonResponse({'status': 'uploaded'})

def process_form(request):
    """Form processing with validation issues."""
    # Issue: no input validation
    name = request.POST.get('name')
    email = request.POST.get('email')

    # Issue: direct HTML output (XSS potential)
    return HttpResponse(f"<h1>Welcome {name}</h1><p>Email: {email}</p>")

# Issue: unused function
def unused_helper():
    """Helper function that's never used."""
    return "helper"

# Issue: poor error handling
def divide_view(request):
    """Division view with no error handling."""
    a = int(request.GET.get('a', 0))
    b = int(request.GET.get('b', 1))

    # Issue: no try/catch
    result = a / b
    return JsonResponse({'result': result})
