from PIL import Image
import numpy as np
import os
import random
import time
from math import log10, sqrt

# File Management
def read_image(path):
    image = Image.open(path)
    image_array = np.array(image)
    image_dim = image_array.shape
    image_array = np.ravel(image_array)
    image.close()

    return image_array, image_dim

def read_file(path):
    f = open(path, 'rb')
    content = f.read()
    f.close()

    return content




# Bitwise Functions
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

def ascii_to_bit(num):
    bit = bin(num)[2:]
    while len(bit)<8:
        bit = '0' + bit
    return bit

def int_to_bit(num):
    bit = bin(num)[2:]
    while len(bit)%8!=0:
        bit = '0' + bit
    return bit

def bit_insertion(num, b):
    return num & 254 | b

def bit_extraction(num):
    return num & 1

def byte_extraction(l):
    bits = ''.join(str(bit_extraction(each)) for each in l)
    return int(bits, 2).to_bytes(1, 'big')

def binary_to_bit(content):
    return ''.join(ascii_to_bit(i) for i in content)

def max_prob(height, width):
    return( ((height-1)*width) + (height*(width -1)) )

def divide_to_planes(bit_array, arr_dim):
    res = []
    remain_col = arr_dim[0] % 8
    remain_row = arr_dim[1] % 8

    max_col = arr_dim[0]//8 + 1
    max_row = arr_dim[1]//8 + 1

    for i in range(max_row):
        temp_arr = []
        for j in range(max_col):
            max_rep = 8 if (i < (max_row-1)) else remain_row
            temp_arr1 = []
            for k in range(max_rep):
                temp_arr2 = bit_array[ ( (i*8 +k)*arr_dim[0] + (j*8) ) : (((i*8 +k)*arr_dim[0] + (j*8) ) + 8)  ] if (j < (max_col-1)) else bit_array[ ( (i*8 +k)*arr_dim[0] + (j*8) ) : (((i*8 +k)*arr_dim[0] + (j*8) ) + remain_col)  ]
                temp_arr1.append(temp_arr2)
            res.append(temp_arr1)
    return res
    

def bpcs_encrypt(image_path, message_path, threshold=0.3):
    return


# Steganography Main Class
class Stegano():
    @staticmethod
    def LSB_encrypt_image(image_path, message_path, key=0):
        # Initialize
        output_file = image_path[:-4] + '-stego' + image_path[-4:]
        image_array, initial_dim = read_image(image_path)

        # Read Message File
        content = read_file(message_path)

        # Message and Description Into Bit
        bits = binary_to_bit(content)
        bits_len = len(bits)
        if key:
            prefix = ascii_to_bit(len(message_path)+128) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)
        else:
            prefix = ascii_to_bit(len(message_path)) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)

        # Initialize Random Pixel List
        idx_list = []
        for i in range(len(prefix), len(image_array)):
            idx_list.append(i)
        if key:
            random.seed(key)
            random.shuffle(idx_list)

        # Insert Message Description
        for i in range(len(prefix)):
            image_array[i] = bit_insertion(image_array[i], int(prefix[i]))

        # Insert Message
        for i, num in enumerate(idx_list):
            if i==bits_len:
                break
            image_array[num] = bit_insertion(image_array[num], int(bits[i]))
        
        # Save Stego Image
        image_array = np.reshape(image_array, initial_dim)

        stego_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        stego_image.save(output_file)
        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_image(stego_path, key=0):
        # Initialize Image List and Content
        stego_array, dim = read_image(stego_path)
        content = bytearray()
        acak = False

        # Get Message File Name
        file_name_len = ord(byte_extraction(stego_array[:8]))
        if file_name_len >= 128:
            file_name_len -= 128
            acak = True
        file_name = ''
        for i in range(file_name_len):
            start = 8*(i+1)
            stego_byte = stego_array[start:8+start]
            stego_char = byte_extraction(stego_byte)
            file_name += stego_char.decode('utf-8')

        # Get Message File Size
        start = 8*(1+file_name_len)
        file_size_len = ord(byte_extraction(stego_array[start:8+start]))
        file_size = 0
        for i in range(file_size_len):
            file_size = file_size << 8
            start = 8*(i+1+file_name_len+1)
            stego_byte = stego_array[start:8+start]
            stego_char = ord(byte_extraction(stego_byte))
            file_size += stego_char
        # print(file_size)
        
        # Initialize acak Pixel List
        idx_list = []
        for i in range((1+file_name_len+1+file_size_len)*8, len(stego_array)):
            idx_list.append(i)
        if key and acak:
            random.seed(key)
            random.shuffle(idx_list)

        # Prune Searching List
        idx_list = idx_list[:file_size]

        # Get Message Content
        while len(idx_list)>0:
            eight_idx = idx_list[:8]
            stego_byte = []
            for idx in eight_idx:
                stego_byte.append(stego_array[idx])
            stego_char = byte_extraction(stego_byte)
            content += stego_char
            idx_list = idx_list[8:]
        
        # Write Message
        f = open(file_name, 'wb')
        f.write(content)
        f.close()
        print('Message File Saved as ' + file_name)

    @staticmethod
    def PSNR_image(ori_arr, stego_arr):
        rms = np.mean((ori_arr - stego_arr) ** 2)
        if(rms == 0):
            return 100
        return 20 * log10(255 / sqrt(rms))

    @staticmethod
    def payload_containable_image_LSB(ori_path, message_path):
        ori_array, ori_dim = read_image(ori_path)
        ori_size = 1
        for each in ori_dim:
            ori_size *= each
            
        message_size = os.stat(message_path).st_size
        message_description_len = 1+len(message_path) + 1+(len(int_to_bit(message_size))/8)

        if ori_size >= (message_description_len+message_size)*8:
            return True
        else:
            return False

# print("============================== Start ==============================")
# start_time = time.time()
# stego = Stegano()

# ori_path = 'LogoITB.png'
# message_path = 'tato.png'
# # stego_path = 'LogoITB-stego.png'
# key = 50

# # if stego.payload_containable_image_LSB(ori_path, message_path):
# #     stego.LSB_encrypt_image(ori_path, message_path, key)
# # stego.LSB_decrypt_image(stego_path, key)

# print("--- %s seconds ---" % (time.time() - start_time))
# print("============================== End ==============================")