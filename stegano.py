from PIL import Image
import numpy as np
import os
import random
import time

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

class Stegano():
    @staticmethod
    def LSB_encrypt_image(image_path, message_path, key=0):
        # Initialize
        output_file = image_path[:-4] + '-stego' + image_path[-4:]
        ori_image = Image.open(image_path)
        image_array = np.array(ori_image)
        ori_initial_dim = image_array.shape
        image_array = np.ravel(image_array)

        # Read Message File
        f = open(message_path, 'rb')
        content = f.read()
        f.close()

        # Message and Description Into Bit
        bits = ''.join(ascii_to_bit(i) for i in content)
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
        image_array = np.reshape(image_array, (ori_initial_dim[0], ori_initial_dim[1], ori_initial_dim[2]))
        stego_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
        stego_image.save(output_file)
        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_image(stego_path, key=0):
        # Initialize Image List and Content
        stego = Image.open(stego_path)
        stego_array = np.array(stego)
        stego_array = np.ravel(stego_array)
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


print("============================== Start ==============================")
start_time = time.time()
stego = Stegano()

ori_path = 'LogoITB.png'
ori_size = os.stat(ori_path).st_size
message_path = 'tato.png'
message_size = os.stat(message_path).st_size
stego_path = 'LogoITB-stego.png'
key = 50


# message_description_len = 1+len(message_path) + 1+(len(int_to_bit(message_size))/8)
# if ori_size >= (message_description_len+message_size)*8:
#     stego.LSB_encrypt_image(ori_path, message_path, key)
#     pass
# else:
#     print('Cover image can not hold the message')
stego.LSB_decrypt_image(stego_path, key)

print("--- %s seconds ---" % (time.time() - start_time))
print("============================== End ==============================")

# 00000001 01011100 11011000