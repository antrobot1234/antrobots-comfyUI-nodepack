import sys
import os


from .utils.globals import DIRECTORY_NAME, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

sys.path.append(COMFY_DIR)
from nodes import KSamplerAdvanced, common_ksampler
import comfy.samplers

GROUP_NAME = "sampling"

class KSamplerWithDenoise(KSamplerAdvanced):
    @classmethod
    def INPUT_TYPES(s):
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

NODE_CLASS_MAPPINGS["sample"] = KSamplerWithDenoise
NODE_DISPLAY_NAME_MAPPINGS["sample"] = "KSampler (Advanced) with Denoise"
