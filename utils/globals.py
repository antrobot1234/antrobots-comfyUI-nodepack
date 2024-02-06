import sys
import os
DIRECTORY_NAME = "antrobots-ComfyUI-nodepack"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_NODES_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
COMFY_DIR = os.path.abspath(os.path.join(CUSTOM_NODES_DIR, '..', '..'))
MAXSIZE = sys.maxsize
MINSIZE = -sys.maxsize

from ..flow_nodes import NODE_CLASS_MAPPINGS as swapClassMappings
from ..flow_nodes import NODE_DISPLAY_NAME_MAPPINGS as swapNodeDisplayNameMappings

from ..image_nodes import NODE_CLASS_MAPPINGS as cropClassMappings
from ..image_nodes import NODE_DISPLAY_NAME_MAPPINGS as cropNodeDisplayNameMappings

from ..sampling_nodes import NODE_CLASS_MAPPINGS as customSamplingClassMappings
from ..sampling_nodes import NODE_DISPLAY_NAME_MAPPINGS as customSamplingNodeDisplayNameMappings

from ..dict_nodes import NODE_CLASS_MAPPINGS as dictClassMappings
from ..dict_nodes import NODE_DISPLAY_NAME_MAPPINGS as dictNodeDisplayNameMappings


NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(swapClassMappings)
NODE_CLASS_MAPPINGS.update(cropClassMappings)
NODE_CLASS_MAPPINGS.update(customSamplingClassMappings)
NODE_CLASS_MAPPINGS.update(dictClassMappings)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(swapNodeDisplayNameMappings)
NODE_DISPLAY_NAME_MAPPINGS.update(cropNodeDisplayNameMappings)
NODE_DISPLAY_NAME_MAPPINGS.update(customSamplingNodeDisplayNameMappings)
NODE_DISPLAY_NAME_MAPPINGS.update(dictNodeDisplayNameMappings)