from PIL import Image
import numpy as np
import os

def str_to_bit(text):
    result = ''
    sep = ''
    for i, b in enumerate(bytearray(text, encoding ='utf-8')):
        if i and sep:
            result += sep
        bit = format(b, 'b')
        while len(bit)<8:
            bit = '0' + bit
        result += bit
    return result

def num_to_bit(num):
    bit = bin(num)[2:]
    while len(bit)<8:
        bit = '0' + bit
    return bit

def bit_insertion(num, b):
    return num & 254 | b

def bit_extraction(num):
    return num & 1

def byte_extraction(l):
    bits = ''.join(str(bit_extraction(each)) for each in l)
    return int(bits, 2).to_bytes(1, 'big')

class Stegano():
    @staticmethod
    def LSB_encrypt(image_path, message_path):
        output_file = image_path[:-4] + '-stego' + image_path[-4:]

        ori_image = Image.open(image_path)
        image_array = np.array(ori_image)
        ori_initial_dim = image_array.shape
        image_array = np.ravel(image_array)

        f = open(message_path, 'rb')
        content = f.read()
        f.close()

        bits = num_to_bit(len(message_path)) +  str_to_bit(message_path) + ''.join(num_to_bit(i) for i in content)

        for idx, b in enumerate(bits):
            image_array[idx] = bit_insertion(image_array[idx], int(b))
        
        image_array = np.reshape(image_array, (ori_initial_dim[0], ori_initial_dim[1], ori_initial_dim[2]))
        stego_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        stego_image.save(output_file)

        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt(ori_path, stego_path):
        ori = Image.open(ori_path)
        stego = Image.open(stego_path)
        ori_array = np.array(ori)
        stego_array = np.array(stego)

        ori_array = np.ravel(ori_array)
        stego_array = np.ravel(stego_array)

        file_name_len = ord(byte_extraction(stego_array[:8]))
        file_name = ''

        ori_array = ori_array[8:]
        stego_array = stego_array[8:]

        content = bytearray()
        
        for i in range(file_name_len):
            ori_byte = ori_array[:8]
            stego_byte = stego_array[:8]

            ori_char = byte_extraction(ori_byte)
            stego_char = byte_extraction(stego_byte)

            file_name += stego_char.decode('utf-8')

            ori_array = ori_array[8:]
            stego_array = stego_array[8:]

        while len(ori_array)>0 and len(stego_array)>0:
            ori_byte = ori_array[:8]
            stego_byte = stego_array[:8]

            ori_char = byte_extraction(ori_byte)
            stego_char = byte_extraction(stego_byte)

            content += stego_char

            ori_array = ori_array[8:]
            stego_array = stego_array[8:]

        f = open(file_name, 'wb')
        f.write(content)
        f.close()

        print('Message File Saved as ' + file_name)

steg = Stegano()

ori_path = 'LogoITB.png'
ori_size = os.stat(ori_path).st_size
message_path = 'tato.png'
message_size = os.stat(message_path).st_size
stego_path = 'LogoITB-stego.png'

l = [1, 0, 0, 0, 1, 0, 0, 1]
l1 = [0, 1, 0, 1, 0, 0, 0, 0]

# steg.LSB_encrypt(ori_path, message_path)
# steg.LSB_decrypt(ori_path, stego_path)