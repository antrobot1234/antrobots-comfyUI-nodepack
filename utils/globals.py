import sys
import os
DIRECTORY_NAME = "antrobots-ComfyUI-nodepack"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_NODES_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
COMFY_DIR = os.path.abspath(os.path.join(CUSTOM_NODES_DIR, '..', '..'))
MAXSIZE = sys.maxsize
MINSIZE = -sys.maxsize

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
class Any(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False