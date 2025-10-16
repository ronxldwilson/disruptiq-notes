# Example Repository for Obfuscation Testing

This directory contains sample code files with various obfuscation patterns that the Obfuscation Checker Agent should detect.

## Files

- `obfuscated.js` - JavaScript file with obfuscation patterns:
  - Single-character variable names
  - Base64 encoded strings
  - Hex encoded characters
  - Minified code patterns

- `obfuscated.py` - Python file with similar obfuscation patterns

- `normal.py` - Clean, well-documented Python code for comparison

- `minified.js` - Heavily minified JavaScript with no comments and compact structure

## Testing

Run the obfuscation checker on this directory to see how it detects various patterns:

```bash
python ../main.py .
```

This should generate findings for the obfuscated files while leaving `normal.py` relatively clean.
