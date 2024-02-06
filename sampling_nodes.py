import sys
import os
import nodes

from utils.globals import DIRECTORY_NAME, COMFY_DIR, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


sys.path.append("COMFY_DIR")
import comfy.samplers
from nodes import common_ksampler

GROUP_NAME = "sampling"

class KSamplerWithDenoise:
    @classmethod
    def INPUT_TYPES(s):
                return {"required":
                    {"model": ("MODEL", ),
                    "add_noise": ("BOOLEAN", {"default": True}),
                    "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                    "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                    "positive": ("CONDITIONING", ),
                    "negative": ("CONDITIONING", ),
                    "latent_image": ("LATENT", ),
                    "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                    "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                    "return_with_leftover_noise": ("BOOLEAN", {"default": False}),
                    "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step":0.01, "round": 0.01})
                     }
                }
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

    def sample(self, model, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise):
        force_full_denoise = True
        if return_with_leftover_noise:
            force_full_denoise = False
        disable_noise = False
        if not add_noise:
            disable_noise = True
        return common_ksampler(model, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise, disable_noise=disable_noise, start_step=start_at_step, last_step=end_at_step, force_full_denoise=force_full_denoise)

NODE_CLASS_MAPPINGS["sample"] = KSamplerWithDenoise
NODE_DISPLAY_NAME_MAPPINGS["sample"] = "KSampler (Advanced) with Denoise"
