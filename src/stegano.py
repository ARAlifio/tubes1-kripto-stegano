from PIL import Image
import numpy as np
from math import log10, sqrt, ceil
import os, random, time
import skvideo.io
import wave
import librosa
import soundfile as sf

# File Management
def read_image(path):
    image = Image.open(path)
    image_array = np.array(image)
    image.close()

    return image_array

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

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def bit_insertion(num, b):
    return num & 254 | b

def bit_extraction(num):
    return num & 1

def byte_extraction(l):
    bits = ''.join(str(bit_extraction(each)) for each in l)
    return int(bits, 2).to_bytes(1, 'big')

def binary_to_bit(content):
    return ''.join(ascii_to_bit(i) for i in content)

def LSB_encrypt(image_array, prefix, content, key=0, reseed=False, random_pixel=False):
    dim = image_array.shape
    image_array = np.ravel(image_array)

    # Initialize Random Pixel List
    idx_list = []
    for i in range(len(prefix), len(image_array)):
        idx_list.append(i)
    if reseed:
        random.seed(key)
    if key and random_pixel:
        random.shuffle(idx_list)

    # Insert Message Description
    for i in range(len(prefix)):
        image_array[i] = bit_insertion(image_array[i], int(prefix[i]))

    # Insert Message
    for i, num in enumerate(idx_list):
        if i==len(content):
            break
        image_array[num] = bit_insertion(image_array[num], int(content[i]))

    image_array = np.reshape(image_array, dim)

    return image_array

def LSB_decrypt(file_name_len, file_size, file_size_len, stego_array, key=0, reseed=False, random_pixel=False):
    # Initialize acak Pixel List
    idx_list = []
    content = bytearray()
    start = 0
    if file_name_len!=0:
        start += 1+file_name_len
    else:
        start += 0
    if file_size_len!=0:
        start += 1+file_size_len
    else:
        start += 0
    for i in range(start*8, len(stego_array)):
        idx_list.append(i)
    if reseed:
        random.seed(key)
    if key and random_pixel:
        random.shuffle(idx_list)

    # Prune Searching List
    idx_list = idx_list[:file_size]

    # Get Message Content
    while len(idx_list)>0:
        # print(len(idx_list))
        eight_idx = idx_list[:8]
        stego_byte = []
        for idx in eight_idx:
            stego_byte.append(stego_array[idx])
        stego_char = byte_extraction(stego_byte)
        content += stego_char
        idx_list = idx_list[8:]

    return content

def read_audio(filename):
    x,_ = librosa.load(filename, sr=16000)
    sf.write('tmp.wav',x,16000)
    file = wave.open('tmp.wav','r')
    data= file.readframes(file.getnframes())
    file.close()
    return Audio(data, file.getnchannels(), file.getsampwidth(), file.getframerate())

def write_audio(filename, audio_obj):
    file = wave.open(filename, "wb")
    file.setnchannels(audio_obj.nchannel)
    file.setsampwidth(audio_obj.sample_width)
    file.setframerate(audio_obj.framerate)
    file.writeframes(audio_obj.data)
    file.close()

class Audio:
    def __init__(self, data, nchannel, sample_width, framerate):
        self.data = data
        self.nchannel = nchannel
        self.sample_width = sample_width
        self.framerate = framerate

def bin_arr_to_bit(content):
    res = []
    for byte in content:
        res.append(ascii_to_bit(byte))
    # print(res)
    return res

def bit_to_int(content):
    res = []
    for bit in content:
        res.append(int(bit,2))
    return res

def bit_to_int1(bit):
    return int(bit,2)

def max_prob(height, width):
    return( (((height-1)*width) + (height*(width -1))))

def divide_to_planes(bit_array, arr_dim):
    # print(len(bit_array))
    res = []
    remain_col = arr_dim[1] % 8
    remain_row = arr_dim[0] % 8

    max_col = arr_dim[1]//8 if (remain_col == 0) else (arr_dim[1]//8 + 1)
    max_row = arr_dim[0]//8 + 1 if (remain_row == 0) else arr_dim[0]//8

    # print(arr_dim[0], arr_dim[1])
    # print(remain_col, remain_row)
    # print(max_col, max_row)
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

def divide_msg_to_planes(message):
    # print(message)
    res = []
    nbBlocks = (len(message) // 8) if(len(message) % 8 == 0) else (len(message) // 8 + 1)
    temp = []
    temp1 = []
    for i in range(nbBlocks):
        # print(message[i])
        temp1.append(message[i])
        if( len(temp1) == 8):
            # print(temp1)
            temp.append(temp1)
            temp1 = []
        if(len(temp) == 8):
            # print(temp)
            res.append(temp)
            temp = []
    return res

def generate_plane_cunjugation(width, height):
    init_bit = "0"
    res = []
    for i in range(height):
        temp = []
        bit = init_bit
        for j in range(width):
            temp.append(bit)
            bit = "1" if(bit == "0") else "0"
        init_bit = "1" if (init_bit == "0") else "0"
        res.append(temp)
    # print(res)
    return res

def conjugate_plane(plane, plane_dim):
    width = plane_dim[0]
    height = plane_dim[1]
    conjugation_plane = generate_plane_cunjugation(width, height)

    for i in range(height):
        # print('i = ', i)
        for j in range(width):
            # print('j = ', j)
            plane[i][j] = str(int(plane[i][j]) ^  int(conjugation_plane[i][j]))
    return plane

def div_planes_per_bits(plane):
    res = []
    # print(plane)
    nbRow = len(plane)
    nbCol = len(plane[0])
    for pos in range(8):
        temp = []
        for i in range(nbRow):
            temp1 = []
            for j in range(nbCol):
                # print(i,j,pos)
                # print(plane[i][j])
                temp1.append(plane[i][j][pos])
            temp.append(temp1)
        res.append(temp)
    return res

def transform_pbc_to_bits(planes):
    res = []
    for row in planes:
        res.append(div_planes_per_bits(row))
    return res

def transform_pbc_cgc(plane, pbc):
    res = plane.copy()
    # print(len(plane))
    nbRow = len(plane)
    for i in range(nbRow):
        nbCol = len(plane[i])
        for j in range(nbCol):
            # print(plane[i][j])
            if( j != 0 and isinstance(plane[i][j], str) ):
                if(pbc):
                    res[i][j] = (plane[i][j-1] ^ plane[i][j])
                    # print(plane[i][j-1], plane[i][j], res[i][j])
                else:
                    res[i][j] = (plane[i][j] ^ plane[i][j-1])
                    # print(plane[i][j-1], plane[i][j], res[i][j])
    return res

# dim = width x height
def isPlaneNoiseRegion(plane, threshold, dim):
    nbChange = 0
    nbRow = len(plane)
    nbCol = len(plane[0])
    # print(nbRow, nbCol)
    for i in range(nbRow):
        for j in range(nbCol):
            # print(i,j)
            if i == 0:
                if j == 0:
                    nbChange += 1 if(plane[i][j] != plane[i][j+1]) else 0
                else:
                    if(j != (nbCol - 1)):
                        nbChange += 1 if(plane[i][j] != plane[i][j+1]) else 0
                    nbChange += 1 if(plane[i][j] != plane[i][j-1]) else 0
                nbChange += 1 if(plane[i][j] != plane[i+1][j]) else 0
            else:
                if j == 0:
                    if(i != (nbRow-1)):
                        nbChange += 1 if(plane[i][j] != plane[i+1][j]) else 0
                    nbChange += 1 if(plane[i][j] != plane[i][j+1]) else 0
                    nbChange += 1 if(plane[i][j] != plane[i-1][j]) else 0
                else:
                    if(i != (nbRow - 1)):
                        if(j != (nbCol - 1)):
                            nbChange += 1 if(plane[i][j] != plane[i][j+1]) else 0
                        nbChange += 1 if(plane[i][j] != plane[i+1][j]) else 0
                    else:
                        if(j != (nbCol - 1)):
                            nbChange += 1 if(plane[i][j] != plane[i][j+1]) else 0
                    nbChange += 1 if(plane[i][j] != plane[i-1][j]) else 0
                    nbChange += 1 if(plane[i][j] != plane[i][j-1]) else 0
    alpha = (nbChange/max_prob(dim[0], dim[1]) / 2)
    # print(nbChange/2, max_prob(dim[0], dim[1]))
    return ( (alpha >= threshold),  alpha)
    #  return if plane is noise region and the alpha of the plane

def insertTo(img, msg):
    # print(img)
    for i in range(len(img[0])):
        for j in range(len(img)):
            # print(msg)
            if(len(msg) == 0):
                break
            img[i][j] = msg.pop(0)

def insertImageToPlane(img, conjugate_map, msg, threshold, idx_list=[]):
    i = 1
    temp_msg = conjugate_map
    types = 0
    for blocks in img:
        isNoise, alpha = isPlaneNoiseRegion(blocks, threshold, [len(blocks[0]), len(blocks)])
        if(isNoise):
            #  insert cojungtion map
            if(types == 0):
                insertTo(blocks, temp_msg)
                types += 1
            elif(types == 1):
                temps = msg[0].pop(0)
                if(len(msg[0]) == 0):
                    types = 2
                insertTo(blocks, temps)
            else:
                break
    return img

def writeTo(text, name):
    with open(name, 'w') as f:
        for item in text:
            f.write("%s\n" % item)

def swap_position(plane, idx_list):
    res = []
    nb = len(idx_list)
    for i in range(1,nb):
        res.append(plane[idx_list[i]])
    return res

def list_to_int(plane):
    res = []
    for arr_bit in plane:
        for bits in arr_bit:
            res.append(bit_to_int1(bits))
    return res

def collapse(plane,dim):
    res = []
    i = 0
    for temp in plane:
        for temp1 in temp:
            for bits in temp1:
                if(isinstance(bits, str)):
                    res.append(bit_to_int1(bits))
                else:
                    temp = list_to_int(bits)
                    for i in temp:
                        res.append(i)
                # res = res.join(bits)
    dif = ((dim[0] * dim[1])-len(res)) * (-1)
    res = np.array(res[:-dif])
    return res
    
# Steganography Main Class
class Stegano():
    @staticmethod
    def LSB_encrypt_image(image_path, message_path, key=0):
        # Initialize
        image_array = read_image(image_path)
        image_type = 'RGB' if len(image_array.shape)==3 else 'L'
        image_path = image_path.split('/')
        output_file = image_path[0] + '/stego/' + image_path[2]

        content = read_file(message_path)

        message_path = message_path.split('/')
        message_path = message_path[-1]

        # Message and Description Into Bit
        bits = binary_to_bit(content)
        bits_len = len(bits)
        if key:
            prefix = ascii_to_bit(len(message_path)+128) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)
        else:
            prefix = ascii_to_bit(len(message_path)) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)

        image_array = LSB_encrypt(image_array, prefix, bits, key, True, key)
        
        # Save Stego Image
        stego_image = Image.fromarray(image_array, image_type)
        stego_image.save(output_file)
        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_image(stego_path, key=0):
        # Initialize Image List and Content
        stego_array = read_image(stego_path)
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
        
        # print(file_name_len)
        # print(file_name)
        # print(file_size_len)
        # print(file_size)
        
        content += LSB_decrypt(file_name_len, file_size, file_size_len, stego_array, key, True, acak)
        
        # print(binary_to_bit(content)[:8])
        # Write Message
        f = open('test/message/' + file_name, 'wb')
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
        ori_array = read_image(ori_path)
        ori_dim = ori_array.shape
        ori_array = np.ravel(ori_array)
        ori_size = 1
        for each in ori_dim:
            ori_size *= each
            
        message_size = os.stat(message_path).st_size
        message_description_len = 1+len(message_path) + 1+(len(int_to_bit(message_size))/8)

        if ori_size >= (message_description_len+message_size)*8:
            return True
        else:
            return False

    @staticmethod
    def LSB_encrypt_video(video_path, message_path,
        key=0, random_frame=False, random_pixel=False
        ):
        frames = skvideo.io.vread(video_path)
        initial_dim = frames.shape

        video_path = video_path.split('/')
        output_file = 'test/stego/' + video_path[-1]
        
        content = read_file(message_path)
        message_path = message_path.split('/')
        message_path = message_path[-1]

        bits = binary_to_bit(content)
        bits_len = len(bits)
        message_code = len(message_path)
        if random_frame:
            message_code += 128
        if random_pixel:
            message_code += 64
        prefix = ascii_to_bit(message_code) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)
        
        frames[0] = LSB_encrypt(frames[0], prefix, '', key, False, False)
        
        frame_size = initial_dim[1] * initial_dim[2] * initial_dim[3]
        reseed = True

        # Initialize Random Pixel List
        idx_list = []
        for i in range(1, initial_dim[0]):
            idx_list.append(i)
        if random_frame:
            random.seed(key)
            random.shuffle(idx_list)

        for i in range(ceil(bits_len/frame_size)):
            current_bits = bits[i*frame_size:(i+1)*frame_size]
            
            frames[idx_list[i]] = LSB_encrypt(frames[idx_list[i]], '', current_bits, key, reseed, random_pixel)

            reseed = False
        
        writer = skvideo.io.FFmpegWriter(output_file,
            outputdict={
                '-vcodec': 'ffv1',
                '-crf': '0',
                '-preset':'veryslow',
                }
            )

        for i in range(len(frames)):
            writer.writeFrame(frames[i])

        writer.close()
        print('Stego Video save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_video(stego_path, key):
        # Initialize
        frames = skvideo.io.vread(stego_path)
        initial_dim = frames.shape

        content = bytearray()
        random_frame, random_pixel = False, False

        # Get Message File Name
        current_frame_array = np.ravel(frames[0])
        file_name_len = ord(byte_extraction(current_frame_array[:8]))
        if file_name_len>=128:
            file_name_len -= 128
            random_frame = True
        if file_name_len>=64:
            file_name_len -= 64
            random_pixel = True
        file_name = ''
        for i in range(file_name_len):
            start = 8*(i+1)
            stego_byte = current_frame_array[start:8+start]
            stego_char = byte_extraction(stego_byte)
            file_name += stego_char.decode('utf-8')
        
        # Get Message File Size
        start = 8*(1+file_name_len)
        file_size_len = ord(byte_extraction(current_frame_array[start:8+start]))
        file_size = 0
        for i in range(file_size_len):
            file_size = file_size << 8
            start = 8*(i+1+file_name_len+1)
            stego_byte = current_frame_array[start:8+start]
            stego_char = ord(byte_extraction(stego_byte))
            file_size += stego_char

        frame_size = initial_dim[1] * initial_dim[2] * initial_dim[3]
        reseed = True

        # Initialize Random Pixel List
        idx_list = []
        for i in range(1, initial_dim[0]):
            idx_list.append(i)
        if random_frame:
            random.seed(key)
            random.shuffle(idx_list)

        for i in range(ceil(file_size/frame_size)):
            current_frame_array = np.ravel(frames[idx_list[i]])
            size = file_size-frame_size if file_size>frame_size else file_size
            content += LSB_decrypt(0, size, 0, current_frame_array, key, reseed, random_pixel)
            reseed = False
            file_size = file_size-frame_size if file_size>frame_size else 0
        
        # Write Message
        f = open('test/message/' + file_name, 'wb')
        f.write(content)
        f.close()
        print('Message File Saved as ' + file_name)

    @staticmethod
    def LSB_encrypt_audio(audio_path, message_path, key=0):
        # Initialize
        audio_obj = read_audio(audio_path)
        audio_path = audio_path.split('/')
        output_file = audio_path[0] + '/stego/' + audio_path[2]

        content = read_file(message_path)

        message_path = message_path.split('/')
        message_path = message_path[-1]

         # Message and Description Into Bit
        bits = binary_to_bit(content)
        bits_len = len(bits)
        if key:
            prefix = ascii_to_bit(len(message_path)+128) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)
        else:
            prefix = ascii_to_bit(len(message_path)) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)

        audio_array = []
        for i in audio_obj.data:
            audio_array.append(i)
        audio_array = np.array(audio_array)
        audio_array = LSB_encrypt(audio_array, prefix, bits, key, True, bool(key))

        audio_after_byte = bytearray()
        for i,each in enumerate(audio_array):
            value = int(each).to_bytes(1, byteorder='big')
            audio_after_byte += value

        audio_obj.data = audio_after_byte

        # Save Stego Audio
        write_audio(output_file,audio_obj)
        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_audio(stego_audio_path, key=0):
        # Initialize Image List and Content
        stego_audio_obj = read_audio(stego_audio_path)

        audio_array = []
        for i in stego_audio_obj.data:
            audio_array.append(i)
        audio_array = np.array(audio_array)

        content = bytearray()
        acak = False

        # Get Message File Name
        file_name_len = ord(byte_extraction(audio_array[:8]))
        if file_name_len >= 128:
            file_name_len -= 128
            acak = True
        file_name = ''
        for i in range(file_name_len):
            start = 8*(i+1)
            stego_byte = audio_array[start:8+start]
            stego_char = byte_extraction(stego_byte)
            file_name += stego_char.decode('utf-8')

        # Get Message File Size
        start = 8*(1+file_name_len)
        file_size_len = ord(byte_extraction(audio_array[start:8+start]))
        file_size = 0
        for i in range(file_size_len):
            file_size = file_size << 8
            start = 8*(i+1+file_name_len+1)
            stego_byte = audio_array[start:8+start]
            stego_char = ord(byte_extraction(stego_byte))
            file_size += stego_char
        
        content += LSB_decrypt(file_name_len, file_size, file_size_len, audio_array, key, True, acak)
        
        # Write Message
        f = open('test/message/' + file_name, 'wb')
        f.write(content)
        f.close()
        print('Message File Saved as ' + file_name)

    @staticmethod
    def LSB_encrypt_audio(audio_path, message_path, key=0):
        # Initialize
        audio_obj = read_audio(audio_path)
        audio_path = audio_path.split('/')
        output_file = audio_path[0] + '/stego/' + audio_path[2]

        content = read_file(message_path)

        message_path = message_path.split('/')
        message_path = message_path[-1]

         # Message and Description Into Bit
        bits = binary_to_bit(content)
        bits_len = len(bits)
        if key:
            prefix = ascii_to_bit(len(message_path)+128) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)
        else:
            prefix = ascii_to_bit(len(message_path)) + str_to_bit(message_path) + ascii_to_bit(int(len(int_to_bit(bits_len))/8)) + int_to_bit(bits_len)

        audio_obj.data = LSB_encrypt(audio_obj, prefix, bits, key, True, key)
        
        # Save Stego Audio
        write_audio(output_file,stego_audio)
        print('Stego File save as: ' + output_file)

    @staticmethod
    def LSB_decrypt_audio(stego_audio_path, key=0):
        # Initialize Image List and Content
        stego_audio_obj = read_audio(stego_audio_path)
        stego_audio_obj.data = np.ravel(stego_audio_obj.data)
        content = bytearray()
        acak = False

        # Get Message File Name
        file_name_len = ord(byte_extraction(stego_audio_obj.data[:8]))
        if file_name_len >= 128:
            file_name_len -= 128
            acak = True
        file_name = ''
        for i in range(file_name_len):
            start = 8*(i+1)
            stego_byte = stego_audio_obj.data[start:8+start]
            stego_char = byte_extraction(stego_byte)
            file_name += stego_char.decode('utf-8')

        # Get Message File Size
        start = 8*(1+file_name_len)
        file_size_len = ord(byte_extraction(stego_audio_obj.data[start:8+start]))
        file_size = 0
        for i in range(file_size_len):
            file_size = file_size << 8
            start = 8*(i+1+file_name_len+1)
            stego_byte = stego_audio_obj.data[start:8+start]
            stego_char = ord(byte_extraction(stego_byte))
            file_size += stego_char
        
        content += LSB_decrypt(file_name_len, file_size, file_size_len, stego_audio_obj.data, key, True, acak)
        
        # Write Message
        f = open('test/message/' + file_name, 'wb')
        f.write(content)
        f.close()
        print('Message File Saved as ' + file_name)

    @staticmethod
    def bpcs_encrypt(image_path, message_path, key=0, threshold=0.3, reseed=False, random_pixel=False):
        # Initialize
        img_arr = read_image(image_path)
        initial_dim = img_arr.shape

        image_type = 'RGB' if len(img_arr.shape)==3 else 'L'
        image_array = np.ravel(img_arr)

        image_path = image_path.split('/')
        output_file = image_path[0] + '/stego/' + image_path[2]

        content = read_file(message_path)

        message_path = message_path.split('/')
        message_path = message_path[-1]

        # transform image array to 8 x 8 pixel array
        img_arr = divide_to_planes(bin_arr_to_bit(image_array), initial_dim)

        # transform image array from pbc to cgc
        cgc_img = transform_pbc_cgc(img_arr, True)

        # transform message byte into bits
        message = bin_arr_to_bit(content)

        # transforms bits message into 8x8 pixel arrays
        msg = divide_msg_to_planes(message)
        plane_msg = []

        for temp_msg in msg:
            plane_msg.append(div_planes_per_bits(temp_msg))
    
        # check if conjugation necessary
        conjugate_map = [] # list of message index with conjugation and message length
        i = 0
        for temp in plane_msg:
            for plane in temp:
                isNoise, alpha = isPlaneNoiseRegion(plane, threshold, [len(plane[0]), len(plane)])
                if(not(isNoise)):
                    plane = conjugate_plane(plane, [len(plane[0]), len(plane)])
                    conjugate_map.append(i)
                i+=1
        conjugate_map.insert(0, len(conjugate_map)) # number of message blocks
        # print(conjugate_map)
                
        # generate random position of message blocks if necessary
        idx_list = list( range(len(plane_msg)) )

        if random_pixel:
            random.shuffle(idx_list)
            idx_list.insert(0, 1)
            swap_position(plane_msg, idx_list)
        
        # insert conjugation map and message
        conjugate_map = bin_arr_to_bit(conjugate_map)

        idx_list = divide_to_planes(bin_arr_to_bit(idx_list), [len(idx_list), 1])

        insertImageToPlane(cgc_img, conjugate_map, plane_msg, threshold, idx_list)

        pbc1 = transform_pbc_cgc(cgc_img, False)

        res = collapse(pbc1,initial_dim)

        res_arr = np.reshape(res, initial_dim)

        stego_image = Image.fromarray(res_arr.astype('uint8'), image_type)
        stego_image.save(output_file)
        print('Stego File save as: ' + output_file)
        

print("============================== Start ==============================")
# start_time = time.time()
# stego = Stegano()

# message_path = 'test/message/tato.png'
# # ori_path = 'test/ori/LogoITB.png'
# # stego_path = 'test/stego/LogoITB.png'
# ori_path = 'test/ori/danau-gs.png'
# # stego_path = 'test/stego/video.avi'
# key = 50
# threshold = 0.3
# # print("============================== Start ==============================")
start_time = time.time()
stego = Stegano()

message_path = 'test/ori/tato.png'
ori_path = 'test/ori/LogoITB.png'
stego_path = 'test/stego/LogoITB.png'
# ori_path = 'test/ori/video.avi'
# stego_path = 'test/stego/video.avi'
# ori_path = 'test/ori/opera.wav'
# stego_path = 'test/stego/opera.wav'
key = 0

# # if stego.payload_containable_image_LSB(ori_path, message_path):
# #     stego.LSB_encrypt_image(ori_path, message_path, key)
stego.LSB_encrypt_image(ori_path, message_path, key)
stego.LSB_decrypt_image(stego_path, key)

# # stego.LSB_encrypt_video(ori_path, message_path, key, True, True)
# # stego.LSB_decrypt_video(stego_path, key)

# stego.LSB_encrypt_audio(ori_path, message_path, key)
# stego.LSB_decrypt_audio(stego_path, key)

# print("--- %s seconds ---" % (time.time() - start_time))
# print("============================== End ==============================")