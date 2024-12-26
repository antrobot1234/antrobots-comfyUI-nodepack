from .utils.globals import DIRECTORY_NAME, Any
from .utils.dict_utils import get_pipe_value
from nodes import ConditioningConcat, KSampler, CLIPTextEncode, CheckpointLoaderSimple

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
GROUP_NAME = "pipe-modifiers"
any = Any("*")


def register(node_class: type, class_name: str, display_name: str):
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name
    node_class.CATEGORY = DIRECTORY_NAME + '/' + GROUP_NAME

    return node_class