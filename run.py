import os
import sys

# Add the project root to the Python path if not already there
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Debugging: Print content of app/__init__.py
try:
    with open(os.path.join(project_root, 'app', '__init__.py'), 'r') as f:
        print("--- Content of app/__init__.py ---")
        print(f.read())
        print("---------------------------------")
except Exception as e:
    print(f"Error reading app/__init__.py: {e}")

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

