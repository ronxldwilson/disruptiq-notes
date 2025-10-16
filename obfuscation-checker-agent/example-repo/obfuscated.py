# Example of obfuscated Python code
a=b=c=1;d=a+b+c;print(d)

def f(x,y,z):return x+y+z
result=f(1,2,3);print(result)

# Base64 encoded string
import base64;encoded="SGVsbG8gV29ybGQ=";print(base64.b64decode(encoded))

# Hex encoded
hex_data=b'\x48\x65\x6c\x6c\x6f';print(hex_data.decode())

# Minified code on one line
class C:def __init__(self,v):self.v=v;def get(self):return self.v;c=C(42);print(c.get())
