from git import Optional
import torch
import sys
import torchvision.transforms.functional as TF
from math import ceil
from .utils.image_utils import *
from PIL import Image

from .utils.globals import DIRECTORY_NAME, MAXSIZE, MINSIZE, COMFY_DIR
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
sys.path.append("COMFY_DIR")
import nodes
import torch
GROUP_NAME = "image-handling"



class CropImageAndMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_in": ("IMAGE",),
                "mask_in": ("MASK",),
                "vertical_padding": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAXSIZE,
                    "step": 1,
                    "display": "number",
                }),
                "horizontal_padding": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAXSIZE,
                    "step": 1,
                    "display": "number",
                }),
                "global_padding": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAXSIZE,
                    "step": 1,
                    "display": "number",
                })
                }
            }
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image_out", "mask_out")
    FUNCTION = "crop"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

    def crop(self,image_in: torch.Tensor, mask_in: torch.Tensor,vertical_padding:int, horizontal_padding:int, global_padding:int) -> tuple[torch.Tensor, torch.Tensor]:
        #convert the mask into a region
        if is_mask_empty(mask_in): return (image_in, mask_in)
        #scale mask to image
        mask_in = scale_to_image(mask_in, image_in)
        box = mask_to_box(mask_in)
        #scale the box to image
        box = scale_box_with_padding(box, horizontal_padding, vertical_padding, image_in.shape[2], image_in.shape[1],global_padding)
        #crop the image and mask
        image_out = crop_with_box(image_in, box)
        mask_out = crop_with_box(mask_in, box)
        #return the cropped image and mask
        return (image_out, mask_out)

class ScaleImageToSize:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image_in": ("IMAGE",),
                             "desired_size": ("INT", {"default": 512, "min": 1, "max": MAXSIZE, "step": 1, "display": "number"}),
                             "doLarger": ("BOOLEAN", {"default": False})}}
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    FUNCTION = "scale"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME

    def scale(self, image_in: torch.Tensor, desired_size: int,doLarger:bool) -> tuple[torch.Tensor]:
        if doLarger:
            scale = desired_size / min(image_in.shape[1], image_in.shape[2])
        else:
            scale = desired_size / max(image_in.shape[1], image_in.shape[2])
        final_size = int(min(image_in.shape[1], image_in.shape[2])*scale)
        size_list = [final_size]
        image_out = scale_to_size(image_in, size_list)
        return (image_out,)
class PasteWithMasks:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"image_source": ("IMAGE",),
                             "mask_source": ("MASK",),
                             "image_dest": ("IMAGE",),
                             "mask_dest": ("MASK",),
                             }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    FUNCTION = "paste"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def paste(self, image_source: torch.Tensor, mask_source: torch.Tensor, image_dest: torch.Tensor, mask_dest: torch.Tensor) -> tuple[torch.Tensor]:
        """
        Paste the source image onto the destination image using masks.

        Args:
            image_source (torch.Tensor): Source image tensor (Batch, Width, Height, Channels).
            mask_source (torch.Tensor): Source mask tensor (Batch, Width, Height).
            image_dest (torch.Tensor): Destination image tensor (Batch, Width, Height, Channels).
            mask_dest (torch.Tensor): Destination mask tensor (Batch, Width, Height).

        Returns:
            torch.Tensor: Resulting image after pasting.
        """
        if is_mask_empty(mask_source): 
            mask_source = scale_to_image(empty_mask(True), image_dest)
        if is_mask_empty(mask_dest): mask_dest = empty_mask(True)
        #scale mask to image
        box = mask_to_box(mask_dest)
        source_box = mask_to_box(mask_source)
        #invert mask_dest
        mask_dest = 1 - mask_dest
        image_source = scale_to_image(image_source, mask_source)
        result_image = alpha_composite(image_source, mask_source, image_dest, None, box[0:2], source_box[0:2])
        return (result_image,)
class AlphaComposite:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"image_source": ("IMAGE",),
                         "image_dest": ("IMAGE",)
                             },
            "optional": {
                        "mask_source": ("MASK",),
                        "mask_dest": ("MASK",),
                        "x_offset": ("INT", {"default": 0, "min": MINSIZE, "max": MAXSIZE, "step": 1, "display": "number"}),
                        "y_offset": ("INT", {"default": 0, "min": MINSIZE, "max": MAXSIZE, "step": 1, "display": "number"})}
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    FUNCTION = "composite"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def composite(self, image_source: torch.Tensor, image_dest: torch.Tensor,mask_source: Optional[torch.Tensor] = None, mask_dest: Optional[torch.Tensor] = None, x_offset: int=0, y_offset: int=0) -> tuple[torch.Tensor]:
        dest = (x_offset,y_offset)
        return (alpha_composite(image_source, mask_source, image_dest, mask_dest, dest),)  # type: ignore
class PreviewMask(nodes.PreviewImage):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                             "mask": ("MASK",),
                             }}
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def save_images(self, mask: torch.Tensor) -> tuple:
        mask_image = mask_to_image(mask)
        return super().save_images(mask_image) # type: ignore
class DialateMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"mask": ("MASK",),
                             "kernel_size": ("INT", {"default": 3, "min": MINSIZE, "max": MAXSIZE, "step": 1})}}
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask_out",)
    FUNCTION = "dialate"
    CATEGORY = DIRECTORY_NAME+'/'+GROUP_NAME
    def dialate(self, mask: torch.Tensor, kernel_size: int) -> tuple[torch.Tensor]:
        return (dialate_mask(mask,kernel_size),)
        





NODE_CLASS_MAPPINGS.update({"crop": CropImageAndMask,
                             "scale": ScaleImageToSize,
                             "paste": PasteWithMasks,
                             "composite": AlphaComposite,
                             "preview_mask": PreviewMask})
                
NODE_DISPLAY_NAME_MAPPINGS.update({"crop": "Crop Image and Mask",
                                    "scale": "Scale Image to Size",
                                    "paste": "Paste with Masks",
                                    "composite": "Alpha Composite",
                                    "preview_mask": "Preview Mask"})