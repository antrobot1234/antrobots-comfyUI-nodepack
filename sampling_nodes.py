import sys
import os


from .utils.globals import DIRECTORY_NAME, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

sys.path.append(COMFY_DIR)
from nodes import KSamplerAdvanced,KSampler, common_ksampler, VAEEncode

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
class KSamplerWithRefiner(KSampler):
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    @classmethod
    def INPUT_TYPES(s):
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

            }
        }
        update["required"].update(types["required"])
        update["required"].pop("model")
        update["required"].pop("steps")
        update["required"].pop("positive")
        update["required"].pop("negative")
        return update
    def sample(self, base_model, refiner_model, total_steps, refine_step, cfg, sampler_name, scheduler, base_positive, base_negative, refine_positive, refine_negative, base_vae, refine_vae, latent_image, seed, denoise=1.0):
        if(refine_step > total_steps):
            refine_step = total_steps
        latent_temp = common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=denoise, start_step=0, last_step=refine_step, force_full_denoise=True)
        image_temp  = base_vae.decode(latent_temp[0]["samples"])
        latent_refine = VAEEncode().encode(refine_vae, image_temp)[0]
        out = common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_refine, denoise=denoise, start_step=refine_step, last_step=total_steps)
        return out
        

NODE_CLASS_MAPPINGS["sample"] = KSamplerWithDenoise
NODE_CLASS_MAPPINGS["refine"] = KSamplerWithRefiner
NODE_DISPLAY_NAME_MAPPINGS["sample"] = "KSampler (Advanced) with Denoise"
NODE_DISPLAY_NAME_MAPPINGS["refine"] = "KSampler with Refiner"
