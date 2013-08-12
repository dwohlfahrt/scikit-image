import numpy as np
from numpy.testing import assert_array_equal
from skimage.filter.inpaint import inpaint_fmm


def test_basic():
    mask = np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8)

    image = np.array(
        [[186, 187, 188, 185, 183, 185, 185, 176, 160, 129, 93, 51, 18, 8, 10],
         [186, 187, 187, 184, 182, 184, 180, 159, 127, 77, 32, 18, 16, 13, 13],
         [185, 185, 185, 184, 184, 183, 174, 146, 107, 59, 18, 10, 13, 12, 13],
         [186, 185, 184, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 12, 14],
         [186, 185, 185, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 14],
         [187, 187, 187, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 15],
         [187, 187, 187, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 13, 13],
         [189, 188, 188, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 13, 11],
         [190, 189, 190, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 10, 10],
         [191, 191, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 9, 10],
         [187, 188, 191, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 10],
         [185, 187, 190, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10],
         [188, 191, 191, 189, 170, 98, 29, 12, 13, 10, 10, 9, 10, 9, 9],
         [192, 196, 194, 174, 140, 76, 19, 10, 16, 13, 11, 10, 11, 9, 9],
         [189, 196, 193, 159, 113, 58, 13, 6, 13, 12, 11, 10, 10, 8, 9]],
        dtype=np.float)

    expected = np.array(
        [[186, 187, 188, 185, 183, 185, 185, 176, 160, 129, 93, 51, 18, 8, 10],
         [186, 187, 187, 184, 182, 184, 180, 159, 127, 77, 32, 18, 16, 13, 13],
         [185, 185, 185, 184, 184, 183, 174, 146, 107, 59, 18, 10, 13, 12, 13],
         [186, 185, 184, 186, 185, 183, 174, 153, 121, 79, 41, 21, 13, 12, 14],
         [186, 185, 185, 185, 185, 184, 172, 150, 117, 71, 22, 18, 13, 13, 14],
         [187, 187, 187, 187, 186, 184, 173, 146, 107, 34, 20, 18, 14, 14, 15],
         [187, 187, 187, 188, 188, 186, 156, 132, 62, 32, 19, 15, 14, 13, 13],
         [189, 188, 188, 189, 187, 183, 153, 108, 61, 28, 15, 12, 15, 13, 11],
         [190, 189, 190, 190, 182, 172, 122, 81, 59, 24, 13, 11, 12, 10, 10],
         [191, 191, 192, 189, 174, 151, 97, 58, 33, 19, 13, 11, 10, 9, 10],
         [187, 188, 191, 184, 171, 128, 77, 41, 24, 15, 12, 9, 9, 9, 10],
         [185, 187, 190, 184, 168, 117, 58, 27, 18, 13, 12, 9, 10, 10, 10],
         [188, 191, 191, 189, 170, 98, 29, 12, 13, 10, 10, 9, 10, 9, 9],
         [192, 196, 194, 174, 140, 76, 19, 10, 16, 13, 11, 10, 11, 9, 9],
         [189, 196, 193, 159, 113, 58, 13, 6, 13, 12, 11, 10, 10, 8, 9]],
        dtype=np.float)

    assert_array_equal(np.round(inpaint_fmm(image, mask, radius=5)), expected)

if __name__ == "__main__":
    np.testing.run_module_suite()
