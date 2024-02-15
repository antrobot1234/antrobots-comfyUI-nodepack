from .utils.globals import DIRECTORY_NAME, Any
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
GROUP_NAME = "dicts"

any = Any("*")
from .utils.image_utils import empty_image, empty_mask, is_mask, is_image, is_latent
from .utils.dict_utils import EntryDict, Entry
import torch
#SET Dict SECTION
def get_first_value(values):
    for value in values:
        return value
def to_tuple(*args):
    out = ()
    for arg in args:
        out += (arg,)
    return out

def set_return_helper(type_name,type_parameters={},type_label=None):
    if type_label is None: type_label = type_name
    return {"required":
                    {
                     "key":("STRING",{"multiline":False}),
                     type_label:(type_name,type_parameters)
                     },
                "optional":
                    {
                     "DICT":("DICT",)
                    }
                } 
def get_return_helper(type_name,default_parameters=None,type_label=None,default_required = False):
    if default_parameters is None: insert = (type_name,)
    else: insert = (type_name,default_parameters)
    out =  {"required":
                    {
                     "key":("STRING",{"multiline":False}),
                     "DICT":("DICT",)
                    }}
    if default_required:
        out["required"]["default"] = insert
    else:
        out["optional"] = {}
        out["optional"]["default"] = insert
    return out
def set_class_constructor(class_name,pretty_name,type_str,type_parameters=None,type_label=None,type_class=None,type_checker=None):
    if type_label is None: type_label = type_str
    @classmethod
    def INPUT_TYPES(s):
        return set_return_helper(type_str,type_parameters,type_label)
    def set(self, key, DICT = {}, **kwargs) -> tuple:
        DICT = EntryDict(DICT)
        DICT[key] = get_first_value(kwargs.values())
        return (DICT,)
    attributes = {
        "INPUT_TYPES":INPUT_TYPES,
        "set":set,
        "RETURN_TYPES":("DICT",),
        "RETURN_NAMES":("DICT",),
        "FUNCTION": "set",
        "CATEGORY": DIRECTORY_NAME+'/'+GROUP_NAME+"/set"
    }
    class_out = type(class_name,(object,),attributes)
    NODE_CLASS_MAPPINGS[class_name] = class_out
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = pretty_name
    return class_out
def get_class_constructor(class_name,pretty_name,type_str,default_parameters = None,type_label=None,type_class=None,type_checker=None,default_replacer=None, default_required = False):
    if type_label is None: type_label = type_str
    @classmethod
    def INPUT_TYPES(s):
        return get_return_helper(type_str,default_parameters,type_label,default_required)
    def get(self,DICT,key,default = None) -> tuple:
        return to_tuple(DICT.get_by_reference(key,Entry(typedef=type_class,default = default)).value)
    attributes = {
        "INPUT_TYPES":INPUT_TYPES,
        "get":get,
        "RETURN_TYPES":(type_str,),
        "RETURN_NAMES":(type_label,),
        "FUNCTION": "get",
        "CATEGORY": DIRECTORY_NAME+'/'+GROUP_NAME+"/get"
    }
    class_out = type(class_name,(object,),attributes)
    NODE_CLASS_MAPPINGS[class_name] = class_out
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = pretty_name
    return class_out
class mergeDicts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                     "DICT1":("DICT",),
                     "DICT2":("DICT",)
                    }
        }
    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("DICT",)
    FUNCTION = "merge"
    def merge(self, DICT1, DICT2):
        DICT1.update(DICT2)
        return (DICT1,)
NODE_CLASS_MAPPINGS["MergeDicts"] = mergeDicts
NODE_DISPLAY_NAME_MAPPINGS["MergeDicts"] = "Merge Dicts"


set_class_constructor("SetDict","Set Dict",any,type_label="any")
set_class_constructor("setDictDict","Set Nested Dict","DICT",type_label="Dict Value",type_class=EntryDict)
set_class_constructor("setDictInt","Set Dict Int","INT",{"default":0},type_class=int)
set_class_constructor("setDictFloat","Set Dict Float","FLOAT",{"default":0.0,"step":0.01},type_class=float)
set_class_constructor("setDictBool","Set Dict Bool","BOOLEAN",{"default":False},type_class=bool)
set_class_constructor("setDictString","Set Dict String","STRING",{"multiline":False},type_class=str)
set_class_constructor("setDictImage","Set Dict Image","IMAGE",type_checker=is_image)
set_class_constructor("setDictMask","Set Dict Mask","MASK",type_checker=is_mask)
set_class_constructor("setDictLatent","Set Dict Latent","LATENT",type_checker=is_latent)
#set_class_constructor("setDictModel","Set Dict Model","MODEL") #check if model?

get_class_constructor("GetDict","Get Dict",any,type_label="any")
get_class_constructor("getDictDict","Get Nested Dict","DICT",type_label="Default",type_class=EntryDict)
get_class_constructor("getDictInt","Get Dict Int","INT",{"default":0},type_class=int)
get_class_constructor("getDictFloat","Get Dict Float","FLOAT",{"default":0.0,"step":0.01},type_class=float)
get_class_constructor("getDictBool","Get Dict Bool","BOOLEAN",{"default":False},type_class=bool)
get_class_constructor("getDictString","Get Dict String","STRING",{"multiline":False},type_class=str)
get_class_constructor("getDictImage","Get Dict Image","IMAGE",type_checker=is_image,default_replacer=empty_image)
get_class_constructor("getDictMask","Get Dict Mask","MASK",type_checker=is_mask,default_replacer=empty_mask)
get_class_constructor("getDictLatent","Get Dict Latent","LATENT",type_checker=is_latent)
#get_class_constructor("getDictModel","Get Dict Model","MODEL")
