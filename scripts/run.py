import sys
import os
import argparse

# Add application top directory
script_path = os.path.join(os.path.dirname(__file__), '..')
app_path = os.path.abspath(script_path)
sys.path.append(app_path)

import library.server as server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Library back end.')
    parser.add_argument('--fake_auth', dest='fake_auth', action='store_true')
    parser.set_defaults(fake_auth=False)
    args = parser.parse_args()
    server.run(args)
