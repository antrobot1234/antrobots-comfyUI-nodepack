import sys
import os
from os.path import dirname as up
DIRECTORY_NAME = "antrobots-ComfyUI-nodepack"
MAXSIZE = sys.maxsize
MINSIZE = -sys.maxsize
NODEPACK_DIR = up(up(__file__))
COMFY_DIR = up(up(NODEPACK_DIR))
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

class Any(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

from ..image_nodes import NODE_CLASS_MAPPINGS as image_nodes
from ..sampling_nodes import NODE_CLASS_MAPPINGS as sampling_nodes
from ..flow_nodes import NODE_CLASS_MAPPINGS as flow_nodes
from ..dict_nodes import NODE_CLASS_MAPPINGS as dict_nodes
from ..pipe_modifiers import NODE_CLASS_MAPPINGS as pipe_modifiers

from ..image_nodes import NODE_DISPLAY_NAME_MAPPINGS as image_nodes_display
from ..sampling_nodes import NODE_DISPLAY_NAME_MAPPINGS as sampling_nodes_display
from ..flow_nodes import NODE_DISPLAY_NAME_MAPPINGS as flow_nodes_display
from ..dict_nodes import NODE_DISPLAY_NAME_MAPPINGS as dict_nodes_display
from ..pipe_modifiers import NODE_DISPLAY_NAME_MAPPINGS as pipe_modifiers_display

NODE_CLASS_MAPPINGS.update(image_nodes)
NODE_CLASS_MAPPINGS.update(sampling_nodes)
NODE_CLASS_MAPPINGS.update(flow_nodes)
NODE_CLASS_MAPPINGS.update(dict_nodes)
NODE_CLASS_MAPPINGS.update(pipe_modifiers)


NODE_DISPLAY_NAME_MAPPINGS.update(image_nodes_display)
NODE_DISPLAY_NAME_MAPPINGS.update(sampling_nodes_display)
NODE_DISPLAY_NAME_MAPPINGS.update(flow_nodes_display)
NODE_DISPLAY_NAME_MAPPINGS.update(dict_nodes_display)
NODE_DISPLAY_NAME_MAPPINGS.update(pipe_modifiers_display)
