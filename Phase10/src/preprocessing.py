import os
from PIL import Image
import numpy as np


def get_best_score(array, code, channels):
    min_score = np.infty
    min_index = -1

    code_len = code.shape[0]
    for i in range(array.shape[0] - (code_len * channels)):
        tmp = array[i: i + (code_len * channels):channels]
        tmp = np.sum(((tmp - code) ** 2))

        if tmp < min_score:
            min_score = tmp
            min_index = i

    return min_index


def write_code(pixels, loc, code):
    pixels[loc[0]:loc[0] + (len(code) * loc[1]):loc[1]] = code
    return pixels


def preprocessing(code_path, image_path, cipher_path):
    with open(code_path, "rb") as f:
        code = f.read()

    image = Image.open(image_path)
    pixels = np.array(image)
    org_shape = pixels.shape
    pixels = pixels.reshape((np.prod(org_shape), ))

    code_ascii = [c for c in code]
    code_ascii.append(0)
    code_arr = np.array(code_ascii)

    loc = get_best_score(pixels, code_arr, org_shape[-1])
    pixels = write_code(pixels, (loc, org_shape[-1]), code_arr)

    new_image = Image.fromarray(pixels.reshape(org_shape), image.mode)
    new_image.save(cipher_path, quality=100)

    return loc


def generate_main(pic_path, loc):
    return """#define STB_IMAGE_IMPLEMENTATION

#include <emscripten.h>
#include <string>
#include <iostream>
#include <sstream>
#include "stb_image.h"

using namespace std;

EM_JS(void, run_code, (const char* str), {
     new Function(UTF8ToString(str))();
});

int main() {
    int x, y, n;
    unsigned char *data = stbi_load("%s",
     &x, &y, &n, 0);
    
    if (!data)
    {
        printf("cannot open image");
        return 1;
    }
    
    int idx = %d;

    ostringstream oss("");

    int i = 0;
    while (data[idx + (i * n)]) {
        oss << data[idx + (i * n)]; 
        i++;
    }
    
    run_code(oss.str().c_str());

    stbi_image_free(data);
}
""" % (pic_path, loc)


def main():
    code_path = r"../code/code.txt"
    image_path = r"../code/img.png"

    folder_name = os.path.dirname(image_path)
    file_name, ext = os.path.splitext(os.path.basename(image_path))
    cipher_path = folder_name + "/" + file_name + "_enc" + ext

    indx = preprocessing(code_path, image_path, cipher_path)

    if cipher_path != "../code/img_enc.png" and cipher_path != "..\\code\\img_enc.png":
        print("Warning! you change the image path. "
              "you need to change the --preload-file flag in build/build_and_run.bat")

    with open("../src/main.cpp", "w") as f:
        f.write(generate_main(cipher_path, indx))


if __name__ == "__main__":
    main()
