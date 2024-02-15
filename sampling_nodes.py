import sys
import torch


from .utils.globals import DIRECTORY_NAME, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

sys.path.append(COMFY_DIR)
from nodes import KSamplerAdvanced,KSampler, common_ksampler, VAEEncode, SetLatentNoiseMask

GROUP_NAME = "sampling"

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
    def sample(self, base_model, refiner_model, total_steps, refine_step, cfg, sampler_name, scheduler, base_positive, base_negative, refine_positive, refine_negative, base_vae, refine_vae, latent_image, seed,base_denoise, refine_denoise, mask: torch.Tensor|None = None):
        if mask != None:
            latent_image = SetLatentNoiseMask.set_mask(None,latent_image, mask)[0] # type: ignore
        if refine_step >= total_steps:
            return (common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=total_steps)[0], base_vae)
        latent_temp = common_ksampler(base_model, seed, total_steps, cfg, sampler_name, scheduler, base_positive, base_negative, latent_image, denoise=base_denoise, start_step=0, last_step=refine_step, force_full_denoise=True)[0]
        if base_vae == refine_vae:
            return common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_temp, denoise=refine_denoise, start_step=refine_step, last_step=total_steps)
        image_temp  = base_vae.decode(latent_temp["samples"])
        latent_refine = VAEEncode().encode(refine_vae, image_temp)[0]
        if mask != None:
            latent_refine = SetLatentNoiseMask.set_mask(None,latent_refine, mask)[0] #type: ignore
        out = common_ksampler(refiner_model, seed, total_steps, cfg, sampler_name, scheduler, refine_positive, refine_negative, latent_refine, denoise=refine_denoise, start_step=refine_step, last_step=total_steps)
        return out + (refine_vae,)
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
        

NODE_CLASS_MAPPINGS["sample"] = KSamplerWithDenoise
NODE_CLASS_MAPPINGS["refine"] = KSamplerWithRefiner
NODE_CLASS_MAPPINGS["calc"] = calcPercentage
NODE_DISPLAY_NAME_MAPPINGS["sample"] = "KSampler (Advanced) with Denoise"
NODE_DISPLAY_NAME_MAPPINGS["refine"] = "KSampler with Refiner"
NODE_DISPLAY_NAME_MAPPINGS["calc"] = "Percentage of Total"
