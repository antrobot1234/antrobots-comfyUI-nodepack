import sys
from typing import Any
from sympy import true
import torch
from .utils.image_utils import empty_mask, is_mask_empty, is_mask_full


from .utils.globals import DIRECTORY_NAME, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

sys.path.append(COMFY_DIR)
from nodes import KSamplerAdvanced,KSampler, common_ksampler, VAEEncode, SetLatentNoiseMask, EmptyLatentImage

GROUP_NAME = "sampling"
def set_latent_noise_mask(mask, latent_image):
    if mask is not None and not is_mask_empty(mask):
        latent_image = SetLatentNoiseMask().set_mask(latent_image, mask)[0]
    return latent_image
def encode_VAE(latent_image : torch.Tensor, vae):
    return VAEEncode().encode(vae, latent_image)[0]
def decode_VAE(latent_image, vae):
    return vae.decode(latent_image["samples"])
def recode_VAE(latent_image, vae_from, vae_to):
    if vae_from == vae_to:
        return latent_image
    return encode_VAE(decode_VAE(latent_image, vae_from), vae_to)
class KSamplerWithDenoise(KSamplerAdvanced):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types["required"].update({"denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step":0.01, "round": 0.01})})
        types["required"]["add_noise"] = ("BOOLEAN", {"default": True})
        types["required"]["return_with_leftover_noise"] = ("BOOLEAN", {"default": False})
        return types
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

    def sample(self, model, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise):
        force_full_denoise = not return_with_leftover_noise
        disable_noise = not add_noise
        out = common_ksampler(model, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise, disable_noise=disable_noise, start_step=start_at_step, last_step=end_at_step, force_full_denoise=force_full_denoise)
        return out
class KSamplerWithRefiner(KSampler):
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        update= {
            "required": {
                "base_model": ("MODEL", {"default": None}),
                "refiner_model": ("MODEL", {"default": None}),
                "total_steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "refine_step": ("INT", {"default": 10, "min": 0, "max": 10000}),
                "base_positive": ("CONDITIONING", {}),
                "base_negative": ("CONDITIONING", {}),
                "refine_positive": ("CONDITIONING", {}),
                "refine_negative": ("CONDITIONING", {}),
                "base_vae": ("VAE", {}),
                "refine_vae": ("VAE", {}),
                "base_denoise":("FLOAT", {"default": 1.0, "min": 0.01, "max": 1.0, "step":0.01, "round": 0.01}),
                "refine_denoise":("FLOAT", {"default": 1.0, "min": 0.01, "max": 1.0, "step":0.01, "round": 0.01}),
            },"optional": {
                "mask": ("MASK", {}),
            }
        }
        update["required"].update(types["required"])
        update["required"].pop("model")
        update["required"].pop("steps")
        update["required"].pop("positive")
        update["required"].pop("negative")
        update["required"].pop("denoise")
        return update
    def sample(self, base_model, refiner_model, total_steps, refine_step, cfg, sampler_name, scheduler, base_positive, base_negative, refine_positive, refine_negative, base_vae, refine_vae, latent_image, seed,base_denoise, refine_denoise, mask: torch.Tensor|None = None) -> tuple[torch.Tensor, Any]:
        if mask is None: mask = empty_mask(True)
        do_denoise = (base_vae != refine_vae) or (not is_mask_full(mask) and not is_mask_empty(mask))
        latent_image = set_latent_noise_mask(mask, latent_image)
        if refine_step >= total_steps:
            return (common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=total_steps)[0], base_vae)
        if refine_step == 0:
            latent_image = recode_VAE(latent_image, base_vae, refine_vae)
            latent_image = set_latent_noise_mask(mask, latent_image)
            return (common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_image, denoise=refine_denoise, start_step=0, last_step=total_steps)[0], refine_vae)
        
        latent_temp = common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=refine_step, force_full_denoise=do_denoise)[0]
        latent_temp = recode_VAE(latent_temp, base_vae, refine_vae)
        latent_temp = set_latent_noise_mask(mask, latent_temp)
        return (common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_temp, denoise=refine_denoise, start_step=refine_step, last_step=total_steps,disable_noise=(not do_denoise))[0], refine_vae)
    RETURN_TYPES = ("LATENT","VAE")
class KSamplerWithPipes(KSamplerWithRefiner):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types["required"]["base_pipe"] = ("BASIC_PIPE", {})
        types["required"]["refine_pipe"] = ("BASIC_PIPE", {})
        types["optional"]["image"] = ("IMAGE", {})
        types["optional"]["use_image"] = ("BOOLEAN", {"default": False})

        types["required"].pop("base_model")
        types["required"].pop("base_positive")
        types["required"].pop("base_negative")
        types["required"].pop("base_vae")

        types["required"].pop("refiner_model")
        types["required"].pop("refine_positive")
        types["required"].pop("refine_negative")
        types["required"].pop("refine_vae")

        types["required"].pop("latent_image")

        return types
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    def sample(self, base_pipe, refine_pipe, total_steps, refine_step, cfg, sampler_name, scheduler, image: torch.Tensor, seed,base_denoise, refine_denoise,use_image, mask: torch.Tensor|None = None) -> tuple[torch.Tensor]:
        base_model = base_pipe[0]
        base_vae = base_pipe[2]
        base_positive = base_pipe[3]
        base_negative = base_pipe[4]

        refiner_model = refine_pipe[0]
        refine_vae = refine_pipe[2]
        refine_positive = refine_pipe[3]
        refine_negative = refine_pipe[4]
        img_width = image.shape[2]
        img_height = image.shape[1]
        if use_image:
            latent_image = encode_VAE(image, base_vae)
            if mask is None: mask = empty_mask(True)
        else:
            latent_image = EmptyLatentImage().generate(img_width, img_height)[0]
            mask = empty_mask(True)
        
        latent, vae_out = super().sample(base_model, refiner_model, total_steps, refine_step, cfg, sampler_name, scheduler, base_positive, base_negative, refine_positive, refine_negative, base_vae, refine_vae, latent_image, seed,base_denoise, refine_denoise, mask)
        image = decode_VAE(latent, vae_out)
        return (image,)

def sample_pass(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, image, vae, denoise = 1.0, use_image = False, mask: torch.Tensor|None = None) -> torch.Tensor:
    if use_image:
        latent_image = encode_VAE(image, vae)
        if mask is not None and not is_mask_empty(mask): latent_image = set_latent_noise_mask(mask, latent_image)
    else:
        latent_image = EmptyLatentImage().generate(image.shape[2], image.shape[1])[0]
    latent_image = common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)[0]
    return decode_VAE(latent_image, vae)
class KsamplerWithPipe(KSampler):
    @classmethod
    def INPUT_TYPES(cls):
        types = super().INPUT_TYPES()
        types["required"].pop("latent_image")
        types["required"].pop("model")
        types["required"].pop("positive")
        types["required"].pop("negative")

        types["required"]["pipe"] = ("BASIC_PIPE", {})
        types["required"]["image"] = ("IMAGE", {})
        types["required"]["use_image"] = ("BOOLEAN", {"default": False})
        types["optional"] = {}
        types["optional"]["mask"] = ("MASK", {})
        return types
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    def sample(self, pipe, **kwargs) -> tuple[torch.Tensor]:
        kwargs["model"] = pipe[0]
        kwargs["positive"] = pipe[3]
        kwargs["negative"] = pipe[4]
        kwargs["vae"] = pipe[2]
        return (sample_pass(**kwargs),)

class calcPercentage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "percentage": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step":0.01, "round": 0.01}),
            }
        }
    RETURN_TYPES = ("INT",)
    FUNCTION = "calc"
    def calc(self, total, percentage):
        return (int(total * percentage),)
    CATEGORY = DIRECTORY_NAME+'/'+'math'
def register(node_class: type,class_name : str, display_name : str):
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name

register(KSamplerWithDenoise,"sample","KSampler (Advanced) with Denoise")
register(KSamplerWithRefiner,"refine","KSampler with Refiner")
register(calcPercentage,"calc","Percentage of Total")
register(KSamplerWithPipes,"refine_pipe","KSampler with Pipes")
register(KsamplerWithPipe,"sample_pipe","KSampler with Pipe")
