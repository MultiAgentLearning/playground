import os
import sys

path_to_server_files = os.getenv('PLAYGROUND_GAME_MANAGER_DIRECTORY')
sys.path.insert(0, path_to_server_files)

from app import app as application