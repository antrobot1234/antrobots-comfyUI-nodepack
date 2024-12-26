
from .utils.globals import DIRECTORY_NAME, Any
from .utils.dict_utils import get_pipe_value
from nodes import ConditioningConcat, KSampler, CLIPTextEncode, CheckpointLoaderSimple

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
            return (None,)
        if conditioning_from is None:
            return (conditioning_to,)
        if conditioning_to is None:
            return (conditioning_from,)
        return super().concat(conditioning_to, conditioning_from)
    
ENCODE_FUNC = CLIPTextEncode().encode
CONCAT_FUNC = OptionalConditioningConcat().concat
class OptionalBasicPipe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{},
            "optional":{
                "model":("MODEL",),
                "clip":("CLIP",),
                "vae":("VAE",),
                "positive":("CONDITIONING",),
                "negative":("CONDITIONING",)
                }
        }
    RETURN_TYPES = ("BASIC_PIPE",)
    RETURN_NAMES = ("pipe",)
    FUNCTION = "pipe"
    def pipe(self, model = None, clip = None, vae = None, positive = None, negative = None):
        return ((model, clip, vae, positive, negative),)
class OptionalEditPipe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{"pipe":("BASIC_PIPE",)},
            "optional":{
                "model":("MODEL",),
                "clip":("CLIP",),
                "vae":("VAE",),
                "positive":("CONDITIONING",),
                "negative":("CONDITIONING",)
            }
        }
    RETURN_TYPES = ("BASIC_PIPE",)
    RETURN_NAMES = ("pipe",)
    FUNCTION = "pipe"
    def pipe(self, pipe, model = None, clip = None, vae = None, positive = None, negative = None):
        #insert any new parameters to the pipe tuple in the correct position
        out = []
        inp = [model, clip, vae, positive, negative] #this is the order for all basic pipes
        for i, n in enumerate(pipe):
            if inp[i] is not None:
                out.append(inp[i])
            else:
                out.append(n)
        return (tuple(out),)
class ConcatConditioningPipe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{
                "pipe":("BASIC_PIPE",),
                },
            "optional":{
                "positive":("CONDITIONING",),
                "negative":("CONDITIONING",),
                "prepend":("BOOLEAN",{"default":False,"tooltip":"prepend the provided conditioning values to the pipe instead of appending them"})
                }
        }
    RETURN_TYPES = ("BASIC_PIPE",)
    RETURN_NAMES = ("pipe",)
    FUNCTION = "concat"
    DESCRIPTION = "Concatenates the provided conditioning values to the pipe, or prepends them if prepend is set to true."
    def concat(self, pipe, prepend = False, positive = None, negative = None):
        pipePositive = get_pipe_value(pipe, "positive")
        pipeNegative = get_pipe_value(pipe, "negative")
        
        #handle if any of the provided conditioning values do not exist
        positiveOut, negativeOut = None, None
        if pipePositive is None: positiveOut = positive
        elif positive is None: positiveOut = pipePositive
        
        if pipeNegative is None: negativeOut = negative
        elif negative is None: negativeOut = pipeNegative

        if prepend:
            conditioningTo = positive, negative
            conditioningFrom = pipePositive, pipeNegative
        else:
            conditioningTo = pipePositive, pipeNegative
            conditioningFrom = positive, negative

        #If the values are already defined, just use them. else, concat the conditioning values and return them
        positiveOut = positiveOut or CONCAT_FUNC(conditioningTo[0], conditioningFrom[0])[0]
        negativeOut = negativeOut or CONCAT_FUNC(conditioningTo[1], conditioningFrom[1])[0]
        return ((pipe[0], pipe[1], pipe[2], positiveOut, negativeOut),)

class EncodeConditioningPipe(ConcatConditioningPipe):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types["optional"]['positive'] = ("STRING",{"multiline":True,"dynamicPrompts":True,"tooltip":"positive text to be encoded into conditioning"})
        types["optional"]['negative'] = ("STRING",{"multiline":True,"dynamicPrompts":True,"tooltip":"negative text to be encoded into conditioning"})
        return types
    def concat(self, pipe, prepend = False, positive = "", negative = ""):
        clip = pipe[1]
        if positive == "": positive = None
        else: positive = ENCODE_FUNC(clip,positive)[0]
        if negative == "": negative = None
        else: negative = ENCODE_FUNC(clip,negative)[0]
        return super().concat(pipe, prepend, positive, negative)

class SamplerPipe(KSampler):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        out = {}
        out["required"] = {}
        out["required"]["cfg"] = types["required"]["cfg"]
        out["required"]["sampler_name"] = types["required"]["sampler_name"]
        out["required"]["scheduler"] = types["required"]["scheduler"]
        return out

    RETURN_TYPES = ("SAMPLER_PIPE",)
    RETURN_NAMES = ("sampler_pipe",)
    FUNCTION = "sampler_pipe"
    def sampler_pipe(self, cfg, sampler_name, scheduler):
        return ((cfg, sampler_name, scheduler),)


class LoadCheckpointToPipe(CheckpointLoaderSimple):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types.setdefault("optional", {})
        types["optional"]["positive"] = ("CONDITIONING",)
        types["optional"]["negative"] = ("CONDITIONING",)
        return types
    RETURN_TYPES = ("BASIC_PIPE","STRING")
    RETURN_NAMES = ("pipe","ckpt_name")
    DESCRIPTION = "Loads a diffusion model checkpoint directly onto a basic pipe. If positive or negative are not provided, they will be None in the pipe."
    OUTPUT_TOOLTIPS = ("The pipe containing the diffusion model, CLIP model, VAE model, positive and negative conditionings.", "The name of the checkpoint file.")
    def load_checkpoint(ckpt_name, positive = None, negative = None):

        model, clip, vae = super().load_checkpoint(ckpt_name)

        return ((model, clip, vae, positive, negative), ckpt_name)
class loadCheckpointWithPrompt(LoadCheckpointToPipe):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types["optional"]["positive"] = ("STRING",{"multiline":True,"dynamicPrompts":True,"tooltip":"positive prompt to be encoded into conditioning"})
        types["optional"]["negative"] = ("STRING",{"multiline":True,"dynamicPrompts":True,"tooltip":"negative prompt to be encoded into conditioning"})
        return types
    DESCRIPTION = "Loads a diffusion model checkpoint directly onto a basic pipe, with the prompts encoded as conditionings."
    def load_checkpoint(ckpt_name, positive = "", negative = ""):
        pipe, ckpt_name = super().load_checkpoint(ckpt_name, None, None)
        clip = get_pipe_value(pipe, "clip")
        positive = ENCODE_FUNC(clip,positive)[0]
        negative = ENCODE_FUNC(clip,negative)[0]
        return ((pipe[0], pipe[1], pipe[2], positive, negative), ckpt_name)

def register(node_class: type,class_name : str, display_name : str):
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name
    node_class.CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

register(Swap, "Swap", "Swap")
register(OptionalConditioningConcat, "OptionalConditioningConcat", "Op. Conditioning (Concat)")
register(OptionalBasicPipe, "OptionalBasicPipeInput", "Op. To Basic Pipe")
register(OptionalEditPipe, "OptionalBasicPipeEdit", "Op. Edit Basic Pipe")
register(SamplerPipe, "SamplerPipe", "Sampler Pipe")
register(ConcatConditioningPipe, "ConcatConditioningPipe", "Concat Conditioning (PIPE)")
register(EncodeConditioningPipe, "EncodeConditioningPipe", "Encode Conditioning (PIPE)")
register(LoadCheckpointToPipe, "LoadCheckpointToPipe", "Load Checkpoint (PIPE)")
register(loadCheckpointWithPrompt, "LoadCheckpointWithPrompt", "Load Checkpoint With Prompt (PIPE)")
