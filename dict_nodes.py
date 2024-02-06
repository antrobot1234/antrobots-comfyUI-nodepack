from .globals import DIRECTORY_NAME
NODE_CLASS_MAPPINGS = {}
GROUP_NAME = "dicts"
from .any import Any
ANY = Any("*")
from .utils.image_utils import empty_image, empty_mask, is_mask, is_image
import torch
class SetDict:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                     "key":("STRING",{"multiline":False}),
                     "value":(ANY,)
                     },
                "optional":
                    {
                     "DICT":("DICT",)
                    }
                }
    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("DICT",)
    FUNCTION = "set"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def set(self, key, value, DICT = None):
        if DICT is None: DICT = {}
        DICT[key] = value
        return (DICT,)
NODE_CLASS_MAPPINGS["Set Dict"] = SetDict
class GetDict:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                     "key":("STRING",{"multiline":False}),
                     "DICT":("DICT",),
                     "default":(ANY,)
                     },
                }
    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("*",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default):
        if key in DICT:
            return (DICT[key],)
        return (default,) 
NODE_CLASS_MAPPINGS["Get Dict"] = GetDict
class GetDictInt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("INT", {"default": 0})
            }
        }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = 0):
        if key in DICT and type(DICT[key]) == int:
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict Int"] = GetDictInt
class GetDictFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },"optional": {
                "default": ("FLOAT", {"default": 0.0})
            }
        }
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = 0.0):
        if key in DICT and type(DICT[key]) == float:
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict Float"] = GetDictFloat
class GetDictBool:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("BOOL", {"default": False})
            }
        }
    RETURN_TYPES = ("BOOL",)
    RETURN_NAMES = ("BOOL",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = False):
        if key in DICT and type(DICT[key]) == bool:
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict Bool"] = GetDictBool
class GetDictString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("STRING", {"default": ""})
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = ""):
        if key in DICT and type(DICT[key]) == str:
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict String"] = GetDictString
class GetDictImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("IMAGE",)
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = empty_image()):
        if key in DICT and is_image(DICT[key]):
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict Image"] = GetDictImage
class GetDictMask:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("MASK",)
            }
        }
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("MASK",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT,default = empty_mask()):
        if key in DICT and is_mask(DICT[key]):
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Dict Mask"] = GetDictMask
class getDictDict:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
            "optional": {
                "default": ("DICT",)
            }
        }
    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("DICT",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def get(self, key, DICT, default = {}):
        if key in DICT and type(DICT[key]) == dict:
            return (DICT[key],)
        return (default,)
NODE_CLASS_MAPPINGS["Get Nested Dict"] = getDictDict
class GetDictUnsafe:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"multiline": False}),
                "DICT": ("DICT",)
            },
        }
    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("value",)
    FUNCTION = "get"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME+'/EXPERIMENTAL'
    def get(self, key, DICT):
        if key in DICT:
            return (DICT[key],)
        else:
            print("Warning: key [", key, "] not found in DICT. Unexpected behavior may occur.")
            return (None,)
NODE_CLASS_MAPPINGS["Get Dict Unsafe"] = GetDictUnsafe