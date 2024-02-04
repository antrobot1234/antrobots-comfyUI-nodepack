DIRECTORY_NAME = "antrobots-ComfyUI-nodepack"

from .flow_nodes import NODE_CLASS_MAPPINGS as swapClassMappings

from .image_nodes import NODE_CLASS_MAPPINGS as cropClassMappings
from .image_nodes import NODE_DISPLAY_NAME_MAPPINGS as cropNodeDisplayNameMappings

from .sampling_nodes import NODE_CLASS_MAPPINGS as customSamplingClassMappings
from .sampling_nodes import NODE_DISPLAY_NAME_MAPPINGS as customSamplingNodeDisplayNameMappings


NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(swapClassMappings)
NODE_CLASS_MAPPINGS.update(cropClassMappings)
NODE_CLASS_MAPPINGS.update(customSamplingClassMappings)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(cropNodeDisplayNameMappings)
NODE_DISPLAY_NAME_MAPPINGS.update(customSamplingNodeDisplayNameMappings)