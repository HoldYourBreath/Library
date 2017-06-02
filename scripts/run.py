import sys
import os

# Add application top directory
script_path = os.path.join(os.path.dirname(__file__), '..')
app_path = os.path.abspath(script_path)
sys.path.append(app_path)

import library.server as server

if __name__ == "__main__":
    server.run()
