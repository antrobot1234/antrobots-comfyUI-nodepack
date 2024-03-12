import sys
from typing import Any
import torch
from .utils.image_utils import is_mask_empty, empty_mask


from .utils.globals import DIRECTORY_NAME, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

sys.path.append(COMFY_DIR)
from nodes import KSamplerAdvanced,KSampler, common_ksampler, VAEEncode, SetLatentNoiseMask

GROUP_NAME = "sampling"
def set_latent_noise_mask(mask, latent_image):
    if mask is not None and not is_mask_empty(mask):
        latent_image = SetLatentNoiseMask().set_mask(latent_image, mask)
def recode_VAE(latent_image, vae_from, vae_to):
    if vae_from == vae_to:
        return latent_image
    return VAEEncode().encode(vae_to,vae_from.decode(latent_image["samples"]))
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
        latent_image =set_latent_noise_mask(mask, latent_image)
        if refine_step >= total_steps:
            return (common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=total_steps)[0], base_vae)
        if refine_step == 0:
            latent_image = recode_VAE(latent_image, base_vae, refine_vae)
            return (common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_image, denoise=refine_denoise, start_step=0, last_step=total_steps)[0], refine_vae)
        
        latent_temp = common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=refine_step, force_full_denoise=False)[0]
        latent_temp = recode_VAE(latent_temp, base_vae, refine_vae)
        latent_temp = set_latent_noise_mask(mask, latent_temp)
        return (common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_temp, denoise=refine_denoise, start_step=refine_step, last_step=total_steps,disable_noise=True)[0], base_vae)
    RETURN_TYPES = ("LATENT","VAE")
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
    node_class.CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME  

register(KSamplerWithDenoise,"sample","KSampler (Advanced) with Denoise")
register(KSamplerWithRefiner,"refine","KSampler with Refiner")
register(calcPercentage,"calc","Percentage of Total")
