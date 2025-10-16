# Test file with detectable secrets

API_KEY = "pk-1234567890abcdef1234567890abcdef"
PASSWORD = "mysecretpassword123"
TOKEN = "token_abcdef123456"

# This should be detected as hardcoded credential
connection = "postgresql://admin:secret123@localhost/db"
