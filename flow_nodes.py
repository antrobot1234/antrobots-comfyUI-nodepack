
from .utils.globals import DIRECTORY_NAME, Any
from nodes import ConditioningConcat
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
GROUP_NAME = "flow-control"
any = Any("*")
class Swap: 
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                    {"val1":(any,),
                     "val2":(any,),
                     "doSwap":("BOOLEAN",)
                     }
                }
    RETURN_TYPES = (any,any)
    RETURN_NAMES = ("valA","valB")
    FUNCTION = "swap"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

    def swap(self, val1, val2, doSwap: bool):
        if doSwap:
            return val2, val1
        else:
            return val1, val2
class OptionalConditioningConcat(ConditioningConcat):
    @classmethod
    def INPUT_TYPES(cls):
        return {
                "required":{},
                "optional":
                    {"conditioning_to":("CONDITIONING",),
                     "conditioning_from":("CONDITIONING",)}
        }
    def concat(self, conditioning_to = None, conditioning_from = None) -> tuple:
        if conditioning_from is None and conditioning_to is None:
            raise Exception("conditioning_to and conditioning_from cannot both be None")
        if conditioning_from is None:
            return (conditioning_to,)
        if conditioning_to is None:
            return (conditioning_from,)
        return super().concat(conditioning_to, conditioning_from)
class OptionalBasicPipe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
                "required":{},
                "optional":{
                    "MODEL":("MODEL",),
                    "CLIP":("CLIP",),
                    "VAE":("VAE",),
                    "POSITIVE":("CONDITIONING",),
                    "NEGATIVE":("CONDITIONING",)
                    }
        }
    def pipe(self, model = None, clip = None, vae = None, positive = None, negative = None):
        return ((model, clip, vae, positive, negative),)
NODE_CLASS_MAPPINGS["Swap"] = Swap
NODE_CLASS_MAPPINGS["OptionalConditioningConcat"] = OptionalConditioningConcat
NODE_DISPLAY_NAME_MAPPINGS["Swap"] = "Swap"
NODE_DISPLAY_NAME_MAPPINGS["OptionalConditioningConcat"] = "Op. Conditioning (Concat)"