#!/usr/bin/env python3
"""
Django manage.py equivalent with issues.
"""

import os
import sys
import subprocess

# Security issue: hardcoded settings
SECRET_KEY = 'django-insecure-dev-key'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

def main():
    """Main function with issues."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    # Issue: using shell=True
    subprocess.run([sys.executable, 'app.py'] + sys.argv[1:], shell=True)

if __name__ == '__main__':
    main()
