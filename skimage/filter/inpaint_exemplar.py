from __future__ import division
import numpy as np
from skimage.util import img_as_float
from skimage.filter._inpaint_criminisi import _inpaint_criminisi


__all__ = ['inpaint_criminisi']


def inpaint_criminisi(source_image, synth_mask, window, max_thresh=0.2):
    """Returns the image with masked pixels reconstructed.

    This function performs constrained synthesis using Criminisi et al. [1]_.
    It grows the texture of the surrounding region to fill in unknown pixels.

    Parameters
    ----------
    source_image : (M, N) array, uint8
        Input image whose texture is to be calculated.
    synth_mask : (M, N) array, bool
        Texture for True values are to be synthesised.
    window : int
        Width of the neighborhood window. (window, window) patch with centre at
        the pixel to be inpainted. Refer to Notes below for details on
        choice of value. Preferably odd, for symmetry.
    max_thresh : float, optional
        Maximum tolerable SSD (Sum of Squared Difference) between the template
        around a pixel to be filled and an equal size image sample for
        template matching.

    Returns
    -------
    image : (M, N) array, float
        Texture synthesised source_image.

    Notes
    -----
    For best results, `window` should be larger in size than the largest texel
    (texture element) being inpainted. A texel is the smallest repeating block
    of pixels in a texture or pattern. For example, in the case below of the
    `skimage.data.checkerboard` image, the single white/black square is the
    largest texel which is of shape `(25, 25)`. A value larger than this yields
    perfect reconstruction, but in case of a value smaller than this perfect
    reconstruction may not be possible.

    References
    ----------
    .. [1] A. Criminisi, P. Perez, and K. Toyama. 2004. Region filling and
           object removal by exemplar-based image inpainting. Trans. Img. Proc.
           13, 9 (September 2004), 1200-1212. DOI=10.1109/TIP.2004.833105.

    Example
    -------
    >>> import numpy as np
    >>> from skimage.data import checkerboard
    >>> from skimage.filter.inpaint_exemplar import inpaint_criminisi
    >>> image = checkerboard().astype(np.uint8)
    >>> mask = np.zeros_like(image, dtype=np.uint8)
    >>> paint_region = (slice(75, 125), slice(75, 125))
    >>> image[paint_region] = 0
    >>> mask[paint_region] = 1
    >>> painted = inpaint_criminisi(image, mask, window=27, max_thresh=0.2)

    """

    source_image = img_as_float(source_image)

    h, w = source_image.shape
    offset = window // 2

    # Padding
    pad_size = (h + window - 1, w + window - 1)
    image = np.zeros(pad_size, dtype=np.float)
    mask = np.zeros(pad_size, np.uint8)

    image[offset:offset + h, offset:offset + w] = source_image
    mask[offset:offset + h, offset:offset + w] = synth_mask

    return _inpaint_criminisi(image, mask, window, max_thresh)
