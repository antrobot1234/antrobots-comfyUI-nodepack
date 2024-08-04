from git import Optional
from sympy import true
import torch
import torchvision.transforms.functional as TF
from torchvision.ops import masks_to_boxes
import PIL.Image as Image
import PIL.ImageFilter as ImageFilter
interp_mode_list = ["nearest","nearest-exact", "bilinear", "bicubic"]
def dialate_mask(mask: torch.Tensor, kernel_size: int = 3) -> torch.Tensor:
    """
    Dilate a mask.

    Args:
        mask (torch.Tensor): The mask to be dilated.
        kernel_size (int, optional): The kernel size for the dilation. Defaults to 3.

    Returns:
        torch.Tensor: The dilated mask.
    """
    #convert mask to PIL image
    mask_img = convert_img_to_pil(mask)
    #dilate mask
    if (kernel_size > 0):
        mask_img = mask_img.filter(ImageFilter.MaxFilter(kernel_size))
    elif (kernel_size < 0):
        mask_img = mask_img.filter(ImageFilter.MinFilter(-kernel_size))
    #convert mask back to torch tensor
    mask = convert_pil_to_img(mask_img,True)
    return mask
def empty_image() -> torch.Tensor:
    """
    Create an empty image tensor.

    Returns:
        torch.Tensor: An empty image tensor with shape (1, 16, 16, 3).
    """
    return torch.zeros((1, 16, 16, 3))
def empty_mask(do_active: bool = False) -> torch.Tensor:
    """
    Create an empty mask tensor. if do_active is True, the mask will be full (white), otherwise it will be empty (black).

    Returns:
        torch.Tensor: An empty mask tensor with shape (1, 16, 16).
    """
    if do_active:
        return torch.ones((1, 16, 16))
    return torch.zeros((1, 16, 16))
def is_image(image: torch.Tensor) -> bool:
    """
    Check if an image is valid.

    Args:
        image (torch.Tensor): The image to be checked.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    return type(image) == torch.Tensor and len(image.shape) == 4 and image.shape[3] == 3
def is_mask(mask: torch.Tensor) -> bool:
    """
    Check if a mask is valid.

    Args:
        mask (torch.Tensor): The mask to be checked.

    Returns:
        bool: True if the mask is valid, False otherwise.
    """
    return type(mask) == torch.Tensor and len(mask.shape) == 3
def is_latent(latent: torch.Tensor) -> bool:
    """
    Check if a latent is valid.

    Args:
        latent (torch.Tensor): The latent to be checked.

    Returns:
        bool: True if the latent is valid, False otherwise.
    """
    return True #TODO learn how latents are stored to determine if the input is a latent
def is_mask_empty(mask: torch.Tensor) -> bool:
    """
    Check if a mask is empty.

    Args:
        mask (torch.Tensor): The mask to be checked.

    Returns:
        bool: True if the mask is empty, False otherwise.
    """
    return bool(mask.sum() == 0)
def is_mask_full(mask: torch.Tensor) -> bool:
    return bool(mask.sum() == mask.numel())
def mask_to_image(mask: torch.Tensor) -> torch.Tensor:
    """
    Convert a mask to an image.

    Args:
        mask (torch.Tensor): The mask to be converted.

    Returns:
        torch.Tensor: The converted image.
    """
    return torch.stack([mask,mask,mask],3)
def box_to_tuple(box: torch.Tensor) -> tuple:
    """
    Convert a box represented as a torch.Tensor to a tuple.

    Args:
        box (torch.Tensor): The box to be converted to a tuple.

    Returns:
        tuple: A tuple representing the box in the format (x1, y1, x2, y2).
    """
    x1, y1, x2, y2 = box
    return (x1, y1, x2, y2)
def merge_bounding_boxes(boxes: torch.Tensor) -> torch.Tensor:
    """
    Merge a list of bounding boxes into a single bounding box.

    Args:
        boxes (torch.Tensor): A tensor containing the bounding boxes. Each row represents a bounding box with four values: x1, y1, x2, y2.

    Returns:
        torch.Tensor: A tensor representing the merged bounding box. The tensor has four values: x1, y1, x2, y2.
    """
    x1 = boxes[:, 0].min()
    y1 = boxes[:, 1].min()
    x2 = boxes[:, 2].max()
    y2 = boxes[:, 3].max()
    return torch.Tensor([x1, y1, x2, y2]).to(torch.int32)
def scale_box_to_minimum_size(box, min_width, min_height, max_x, max_y,padding):
    """
    Scales the input box to the minimum specified size while ensuring it fits within the specified maximum dimensions and applies the specified padding. 

    Args:
        box: A tuple representing the coordinates of the box in the format (x1, y1, x2, y2).
        min_width: The minimum width that the box should have.
        min_height: The minimum height that the box should have.
        max_x: The maximum x-coordinate for the box.
        max_y: The maximum y-coordinate for the box.
        padding: The amount of padding to be applied to the box.

    Returns:
        torch.Tensor: A tensor containing the scaled coordinates of the box in the format [x1, x2, y1, y2].
    """
    half_padding = padding
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    x1 = max(0, (x1 - max(0,min_width - width) // 2) - half_padding)
    x2 = min(max_x, (x2 + max(0,min_width - width) // 2) + half_padding)
    y1 = max(0, (y1 - max(0,min_height - height) // 2) - half_padding)
    y2 = min(max_y, (y2 + max(0,min_height - height) // 2) + half_padding)

    return torch.Tensor([x1, y1, x2, y2]).to(torch.int32)
def scale_box_with_padding(box, horizontal_padding, vertical_padding, max_x, max_y, padding):
    """
    Scales the input box while applying the specified padding to the sides of the box.

    Args:
        box: A tuple representing the coordinates of the box in the format (x1, y1, x2, y2).
        horizontal_padding: The amount of padding to be applied to the left and right sides of the box.
        vertical_padding: The amount of padding to be applied to the top and bottom sides of the box.
        max_x: The maximum x-coordinate for the box.
        max_y: The maximum y-coordinate for the box.
        padding: The amount of padding to be applied to the box.

    Returns:
        torch.Tensor: A tensor containing the scaled coordinates of the box in the format [x1, x2, y1, y2].
    """
    x1, y1, x2, y2 = box
    x1 = min(max(0, x1 - horizontal_padding- padding) , max_x)
    x2 = min(max(0, x2 + horizontal_padding+ padding) , max_x)
    y1 = min(max(0, y1 - vertical_padding- padding) , max_y)
    y2 = min(max(0, y2 + vertical_padding+ padding) , max_y)
    return torch.Tensor([x1, y1, x2, y2]).to(torch.int32)

def convert_img_to_bcHW(img:torch.Tensor) -> torch.Tensor:
    """
    Function to convert an image tensor from BWHC (batch, height, width, channels) format to BCWH (batch, channels, height, width) format.
    
    Args:
        img (torch.Tensor): The input image tensor in BWHC format.
        
    Returns:
        torch.Tensor: The converted image tensor in BCWH format.
    """
    return img.permute(0, 3, 1, 2)
def convert_img_to_bHWc(img:torch.Tensor) -> torch.Tensor:
    """
    Convert the input image tensor from BCWH (batch, channels, height, width) format to BWHC (batch, height, width, channels) format.

    Args:
        img (torch.Tensor): The input image tensor in BCWH format.

    Returns:
        torch.Tensor: The image tensor converted to BWHC format.
    """
    return img.permute(0, 2, 3, 1)

def scale_to_image(image_scale:torch.Tensor, image_reference:torch.Tensor, scale_mode: TF.InterpolationMode = TF.InterpolationMode.BILINEAR) -> torch.Tensor:
    """
    Scale the input image or mask to match the size of the reference image and return the scaled image.
    
    Args:
    - image_scale: torch.Tensor, the input image to be scaled
    - image_reference: torch.Tensor, the reference image to match the size
    
    Returns:
    - torch.Tensor, the scaled image
    """
    shape = list((image_reference.shape[1], image_reference.shape[2]))
    if(len(image_scale.shape) == 4):
        image_scale = convert_img_to_bcHW(image_scale)
        image_scale = TF.resize(image_scale, shape, interpolation=scale_mode)
        return convert_img_to_bHWc(image_scale,)
    resized = TF.resize(image_scale, shape, interpolation=scale_mode)
    return resized
def scale_to_size(image_scale:torch.Tensor, desired_size: list[int],scale_mode: TF.InterpolationMode = TF.InterpolationMode.BILINEAR) -> torch.Tensor:
    """
    Scale the input image or mask to match the size of desired_size (maintaining aspect ratio) and return the scaled image.
    
    Args:
    - image_scale: torch.Tensor, the input image to be scaled
    - desired_size: list[int], the desired size of the output image in the format [height, width]
    
    Returns:
    - torch.Tensor, the scaled image
    """
    if(len(image_scale.shape) == 4):
        image_scale = convert_img_to_bcHW(image_scale)
        return convert_img_to_bHWc(TF.resize(image_scale, desired_size, interpolation=scale_mode))
    return TF.resize(image_scale, desired_size, interpolation=scale_mode)
def scale_by_factor(image_scale:torch.Tensor, factor_tuple: tuple, scale_mode: TF.InterpolationMode = TF.InterpolationMode.BILINEAR) -> torch.Tensor:
    """
    Scale the input image by a factor and return the scaled image."""
    factor_y, factor_x = factor_tuple
    if(len(image_scale.shape) == 4):
        image_scale = convert_img_to_bcHW(image_scale)
        return convert_img_to_bHWc(TF.resize(image_scale, (int(image_scale.shape[2] * factor_y), int(image_scale.shape[3] * factor_x)), interpolation=scale_mode))
    return TF.resize(image_scale, (int(image_scale.shape[1] * factor_y), int(image_scale.shape[2] * factor_x)), interpolation=scale_mode)
    
def get_box_factor(box_a:torch.Tensor, box_b:torch.Tensor) -> torch.Tensor:
    """gets the scale factor between box_a and box_b"""
    #get box dimensions
    height_a = box_a[3] - box_a[1]
    width_a = box_a[2] - box_a[0]
    height_b = box_b[3] - box_b[1]
    width_b = box_b[2] - box_b[0]
    return (height_b/height_a, width_b/width_a)
def crop_with_box(image:torch.Tensor, box:torch.Tensor) -> torch.Tensor:
    """
    Crop an image or mask using the specified bounding box.

    Args:
        image (torch.Tensor): The input image tensor.
        box (torch.Tensor): The bounding box coordinates.

    Returns:
        torch.Tensor: The cropped image tensor.
    """
    xmin, ymin, xmax, ymax = box.tolist()
    if(len(image.shape) == 4):
        image = convert_img_to_bcHW(image)
        cropped = TF.crop(image, ymin, xmin, ymax - ymin, xmax - xmin)
        return convert_img_to_bHWc(cropped)
    return TF.crop(image, ymin, xmin, ymax - ymin, xmax - xmin)
def scale_to_box(image:torch.Tensor, box:torch.Tensor,scale_mode: TF.InterpolationMode = TF.InterpolationMode.BILINEAR) -> torch.Tensor:
    """
    Scale an image or mask to match the size of the bounding box.

    Args:
        image (torch.Tensor): The input image tensor.
        box (torch.Tensor): The bounding box coordinates.

    Returns:
        torch.Tensor: The scaled image tensor.
    """
    x1, y1, x2, y2 = box.tolist()
    shape = list((y2 - y1, x2 - x1))
    if(len(image.shape) == 4):
        image = convert_img_to_bcHW(image)
        return convert_img_to_bHWc(TF.resize(image, shape, interpolation=scale_mode))
    return TF.resize(image, shape, interpolation=scale_mode)
def mask_to_box(mask:torch.Tensor) -> torch.Tensor:
    """
    Convert a binary mask to a bounding box.

    Args:
        mask (torch.Tensor): The binary mask tensor.

    Returns:
        torch.Tensor: The bounding box coordinates in the format [x1, y1, x2, y2].
    """
    #convert mask to boxes
    boxes = masks_to_boxes(mask)
    #merge boxes
    box = merge_bounding_boxes(boxes)
    return box
def convert_img_to_pil(image:torch.Tensor) -> Image.Image:
    """
    Convert an image tensor to a PIL image.

    Args:
        image (torch.Tensor): The input image tensor.

    Returns:
        PIL.Image.Image: The converted PIL image.
    """
    if(len(image.shape) == 4):
        image = convert_img_to_bcHW(image)
        return TF.to_pil_image(image[0])
    return TF.to_pil_image(image[0])
def convert_pil_to_img(image:Image.Image,is_mask:bool = False) -> torch.Tensor:
    """
    Convert a PIL image to an image tensor.

    Args:
        image (PIL.Image.Image): The input PIL image.

    Returns:
        torch.Tensor: The converted image tensor.
    """
    tensor = TF.to_tensor(image)
    if not is_mask:
        tensor = tensor.unsqueeze(0)
        tensor = convert_img_to_bHWc(tensor)
    return tensor
def alpha_composite(image_source:torch.Tensor, mask_source:torch.Tensor, image_dest:torch.Tensor, mask_dest: Optional[torch.Tensor], dest = (0,0), source = (0,0)) -> torch.Tensor:
    #convert to numpy if needed
    if(type(dest) == torch.Tensor): dest = tuple(dest.tolist())
    if(type(source) == torch.Tensor): source = tuple(source.tolist())        
    #convert to pil
    image_dest_pil = convert_img_to_pil(image_dest)
    image_source_pil = convert_img_to_pil(image_source)
    #add alpha
    if mask_dest is not None:
        mask_dest = scale_to_image(mask_dest, image_dest)
        mask_dest_img = convert_img_to_pil(mask_dest)
        image_dest_pil.putalpha(mask_dest_img)
    else:
        image_dest_pil.putalpha(Image.new('L', image_dest_pil.size, 255))
    if mask_source is not None:
        mask_source = scale_to_image(mask_source, image_source)
        mask_source_img = convert_img_to_pil(mask_source)
        image_source_pil.putalpha(mask_source_img)
    else:
        image_source_pil.putalpha(Image.new('L', image_source_pil.size, 255))
    #alpha composite
    image_dest_pil.alpha_composite(image_source_pil,dest,source)
    return convert_pil_to_img(image_dest_pil)

    