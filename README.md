
# antrobots ComfyUI Nodepack
welcome to my node pack! This pack serves as a compilation of all the custom nodes I have and will create, with the goal of implementing functionality that I find lacking or obtuse. If you experience any issues with this node pack, please make a github issue! any help finding potential bugs or errors is greatly appreciated.

Below is a description of what each node in this node pack does.

## Sampling Nodes
### KSampler (advanced) with denoise
this node is a variant of the built-in KSampler (advanced) with the additional ability to provide a `denoise` value. This allows you to swap models mid generation in img-to-img workflows much more efficiently. `denoise` works in tandem with `start step` and `end step`.
## Ksampler with Refiner
This node is an extension of the Ksampler (advanced) node that takes in two sets of model parameters. It will then generate with `base_model` until `refine_step`, in which it will switch to `refine_model` (re-encoding the latent with `refine_vae` if the two passed in VAEs are different). it also has an optional `mask` can also be provided, which will set the latent noise mask if given.
## Flow Control nodes
### Swap
This node takes two inputs of any type. If the swap bool is `False`, it simply pipes input 1 into output A and input 2 into output B. however, if the swap bool is `True`, it swaps the outputs, mapping 1 to B and 2 to A. This is useful when combined with piping workflows, as it allows you to easily and quickly switch to a different input pipe or swap two pipes around with a boolean.
## Image Handling Nodes
### Crop Image and Mask:
This node is used to crop an image and its corresponding mask.  It takes an image, a mask, a minimum width, a minimum height, and padding as inputs. It scales the mask to the image, converts the mask into a region, scales the box to the image, and crops the image and mask. If the mask is empty, it returns the input image and mask as they are.
 ### Scale Image to Size: 
This node is used to scale an image to a desired size.  It takes an image, a desired size, and a boolean value  `doLarger`  as inputs. It calculates the scale factor based on the desired size and the smaller or larger dimension of the image (depending on the  `doLarger`  value), scales the image to the final size, and returns the scaled image.
    
 ### Paste with Masks:
 This node is used to paste a source image onto a destination image using masks. It takes a source image, a source mask, a destination image, and a destination mask as inputs, as well as a horizontal padding, a vertical padding, and a global padding. It treats the source mask as an `Alpha` channel for the source image. it then pastes the source image onto the destination image using the destination mask as the area to paste onto, cropping and resizing if necessary. The output mask and image are padded with the horizontal and vertical padding values. Global padding can also be used to pad both width and height at once.
    
### Alpha Composite:
This node is used to composite a source image and a destination image using alpha blending. It takes a source image, a destination image, a source mask, a destination mask, an x offset, and a y offset as inputs. It pastes the source image onto the destination image with offsets, treating the respective masks as alpha channels. Both source mask and destination mask are optional. If either is not provided, the respective image will be pasted as is.

##Dict Nodes
These are various nodes that can pack information into dicts to be sent around and parsed as an alternative workflow to piping.
### Set Dict
This is the core of how these nodes work. any value put into this node will be packaged into a `DICT` labeled as `key` and sent out. A `dict` can optionally be passed in, in which case it will instead append the value to the input dict.
## Get Dict
This node takes in a `DICT`, a `key`, and a `default` value as inputs. if `key` is found in the `DICT`, it will pass it out to the `*` output. otherwise, `default` will be used

## Get Dict **TYPE**
This entry describes all of the nodes that follow this format, as their core functionality is the same. These nodes behave similar to thee standard Get Dict, with two exceptions.
1.  `default` is optional. if default is not provided, a standard default for the type will be provided automatically.
2. inputs are validated with their type. If the input is not of the correct type, `default` will be used instead.

## Get Dict Unsafe
This is a special variant of `get dict` with NO `default`. If the input does not exist, it will return `None`. This can be useful if you are using a lot of custom types and don't want to populate all the defaults. Note that if the key does not exist, most workflows will likely break, so use with caution.