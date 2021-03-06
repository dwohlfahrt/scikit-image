#cython: cdivision=True
#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
import numpy as np
cimport numpy as cnp
from libc.math cimport sin, cos, abs
from skimage._shared.interpolation cimport bilinear_interpolation


def _glcm_loop(cnp.uint8_t[:, ::1] image, double[:] distances,
               double[:] angles, Py_ssize_t levels,
               cnp.uint32_t[:, :, :, ::1] out):
    """Perform co-occurrence matrix accumulation.

    Parameters
    ----------
    image : ndarray
        Input image, which is converted to the uint8 data type.
    distances : ndarray
        List of pixel pair distance offsets.
    angles : ndarray
        List of pixel pair angles in radians.
    levels : int
        The input image should contain integers in [0, levels-1],
        where levels indicate the number of grey-levels counted
        (typically 256 for an 8-bit image)
    out : ndarray
        On input a 4D array of zeros, and on output it contains
        the results of the GLCM computation.

    """

    cdef:
        Py_ssize_t a_idx, d_idx, r, c, rows, cols, row, col
        cnp.uint8_t i, j
        cnp.float64_t angle, distance

    rows = image.shape[0]
    cols = image.shape[1]

    for a_idx in range(len(angles)):
        angle = angles[a_idx]
        for d_idx in range(len(distances)):
            distance = distances[d_idx]
            for r in range(rows):
                for c in range(cols):
                    i = image[r, c]

                    # compute the location of the offset pixel
                    row = r + <int>(sin(angle) * distance + 0.5)
                    col = c + <int>(cos(angle) * distance + 0.5)

                    # make sure the offset is within bounds
                    if row >= 0 and row < rows and \
                       col >= 0 and col < cols:
                        j = image[row, col]

                        if i >= 0 and i < levels and \
                           j >= 0 and j < levels:
                            out[i, j, d_idx, a_idx] += 1


cdef inline int _bit_rotate_right(int value, int length):
    """Cyclic bit shift to the right.

    Parameters
    ----------
    value : int
        integer value to shift
    length : int
        number of bits of integer

    """
    return (value >> 1) | ((value & 1) << (length - 1))


def _local_binary_pattern(double[:, ::1] image,
                          int P, float R, char method='D'):
    """Gray scale and rotation invariant LBP (Local Binary Patterns).

    LBP is an invariant descriptor that can be used for texture classification.

    Parameters
    ----------
    image : (N, M) double array
        Graylevel image.
    P : int
        Number of circularly symmetric neighbour set points (quantization of
        the angular space).
    R : float
        Radius of circle (spatial resolution of the operator).
    method : {'D', 'R', 'U', 'V'}
        Method to determine the pattern.

        * 'D': 'default'
        * 'R': 'ror'
        * 'U': 'uniform'
        * 'V': 'var'

    Returns
    -------
    output : (N, M) array
        LBP image.
    """

    # texture weights
    cdef int[:] weights = 2 ** np.arange(P, dtype=np.int32)
    # local position of texture elements
    rr = - R * np.sin(2 * np.pi * np.arange(P, dtype=np.double) / P)
    cc = R * np.cos(2 * np.pi * np.arange(P, dtype=np.double) / P)
    cdef double[:] rp = np.round(rr, 5)
    cdef double[:] cp = np.round(cc, 5)

    # pre-allocate arrays for computation
    cdef double[:] texture = np.zeros(P, dtype=np.double)
    cdef char[:] signed_texture = np.zeros(P, dtype=np.int8)
    cdef int[:] rotation_chain = np.zeros(P, dtype=np.int32)

    output_shape = (image.shape[0], image.shape[1])
    cdef double[:, ::1] output = np.zeros(output_shape, dtype=np.double)

    cdef Py_ssize_t rows = image.shape[0]
    cdef Py_ssize_t cols = image.shape[1]

    cdef double lbp
    cdef Py_ssize_t r, c, changes, i
    for r in range(image.shape[0]):
        for c in range(image.shape[1]):
            for i in range(P):
                texture[i] = bilinear_interpolation(&image[0, 0], rows, cols,
                                                    r + rp[i], c + cp[i],
                                                    'C', 0)
            # signed / thresholded texture
            for i in range(P):
                if texture[i] - image[r, c] >= 0:
                    signed_texture[i] = 1
                else:
                    signed_texture[i] = 0

            lbp = 0

            # if method == 'uniform' or method == 'var':
            if method == 'U' or method == 'V':
                # determine number of 0 - 1 changes
                changes = 0
                for i in range(P - 1):
                    changes += abs(signed_texture[i] - signed_texture[i + 1])

                if changes <= 2:
                    for i in range(P):
                        lbp += signed_texture[i]
                else:
                    lbp = P + 1

                if method == 'V':
                    var = np.var(texture)
                    if var != 0:
                        lbp /= var
                    else:
                        lbp = np.nan
            else:
                # method == 'default'
                for i in range(P):
                    lbp += signed_texture[i] * weights[i]

                # method == 'ror'
                if method == 'R':
                    # shift LBP P times to the right and get minimum value
                    rotation_chain[0] = <int>lbp
                    for i in range(1, P):
                        rotation_chain[i] = \
                            _bit_rotate_right(rotation_chain[i - 1], P)
                    lbp = rotation_chain[0]
                    for i in range(1, P):
                        lbp = min(lbp, rotation_chain[i])

            output[r, c] = lbp

    return np.asarray(output)
