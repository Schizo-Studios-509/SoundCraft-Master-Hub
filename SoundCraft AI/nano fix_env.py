import sys, os

user_path = os.path.expanduser('~/Documents/lib/python3.10/site-packages')
if user_path not in sys.path:
    sys.path.insert(0, user_path)

print("✅ Using user packages from:", user_path)

try:
    import pathspec
    print("Pathspec version:", pathspec.__version__)
except Exception as e:
    print("Error loading pathspec:", e)