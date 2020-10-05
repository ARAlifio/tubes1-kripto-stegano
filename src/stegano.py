from PIL import Image
import numpy as np
from math import log10, sqrt, ceil
import os, random, time
import skvideo.io
import wave

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
    start = 1+file_name_len if file_name_len!=0 else 0
    start += 1+file_size_len if file_size_len!=0 else 0
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
        eight_idx = idx_list[:8]
        stego_byte = []
        for idx in eight_idx:
            stego_byte.append(stego_array[idx])
        stego_char = byte_extraction(stego_byte)
        content += stego_char
        idx_list = idx_list[8:]

    return content

def read_audio(filename):
    file = wave.open(filename, "rb")
    data = file.readframes(file.getnframes())
    file.close()
    return Audio(data, file.getnchannels(), file.getsampwidth(), file.getframerate())

def write_audio(filename, audio_obj):
    file = wave.open(filename, "wb")
    file.setnchannels(audio_obj.nchannel)
    file.setsampwidth(audio_obj.sampwidth)
    file.setframerate(audio_obj.framerate)
    file.writeframes(audio_obj.data)
    file.close()

class Audio:
    def __init__(self, data, nchannel, sample_width, framerate):
        self.data = data
        self.nchannel = nchannel
        self.sample_width = sample_width
        self.framerate = framerate

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
        stego_image = Image.fromarray(image_array.astype('uint8'), image_type)
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
        # print(file_size)
        
        content += LSB_decrypt(file_name_len, file_size, file_size_len, stego_array, key, True, acak)
        
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

print("============================== Start ==============================")
start_time = time.time()
stego = Stegano()

message_path = 'test/ori/tato.png'
# ori_path = 'test/ori/LogoITB.png'
# stego_path = 'test/stego/LogoITB.png'
# ori_path = 'test/ori/video.avi'
# stego_path = 'test/stego/video.avi'
ori_path = 'test/ori/opera.wav'
stego_path = 'test/stego/opera.wav'
key = 0

# if stego.payload_containable_image_LSB(ori_path, message_path):
#     stego.LSB_encrypt_image(ori_path, message_path, key)
# stego.LSB_decrypt_image(stego_path, key)

# stego.LSB_encrypt_video(ori_path, message_path, key, True, True)
# stego.LSB_decrypt_video(stego_path, key)

# stego.LSB_encrypt_audio(ori_path, message_path, key)
# stego.LSB_decrypt_audio(stego_path, key)

print("--- %s seconds ---" % (time.time() - start_time))
print("============================== End ==============================")