import numpy as np
import random
import re
import string
import binascii

# matrix for full vigene cipher --> save to external file
# full_chip_matrix = np.empty((26,26))
MAX_MATRIX_SIZE = 26
DECRYPTION_ERROR = "Please encrypt first before proceeding to decryption process"
DIVIDE_SIZE = 5

def load_plain_text(filename):
    text = ""
    with open(filename) as files:
        text = files.read() 
    return text

def save_file(filename, text):
    with open(filename, 'w') as files:
        files.write(text)

# clear non alphbet characters for standard vigenere and playfair cipher
def clear_text(text):
    pattern = re.compile('[^a-zA-Z]')
    return pattern.sub('', text)

#generate key for encryption and decryption by repeating input key
def generate_key_repeat(text, key):
    new_key = ''
    if len(text) >= len(key):
        res = len(key) - len(text) % len(key)
        diff = (len(text) // len(key)) + (1 if res != 0 else 0)
        new_key = key*diff
        new_key = new_key[:(len(new_key)-res)]
    else:
        new_key = key[: len(text)]
    return new_key

def generate_full_vigenere_key():
    selected_keys = []
    key = ""
    while(len(key) < 26):
            random_char = random.choice(string.ascii_uppercase)
            if not random_char in key:
                key += random_char
    for item in key:
        selected_keys.append(list(item))
    
    while(len(selected_keys[0])<26):
        it = 0
        selected_chars = []
        random_char = ""
        for item in selected_keys:
            random_char = random.choice(string.ascii_uppercase)
            while (random_char in selected_chars or random_char in item):
                random_char = random.choice(string.ascii_uppercase)
            item += random_char
        # print(selected_keys)

    # print(selected_keys)
    return selected_keys

def alpha_to_num(value):
    return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.index(value)

def num_to_alpha(value):
    return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[value]

def split_text(text, length):
    result = []

    while text:
        result.append(text[:length])
        text = text[length:]

    return result

def playfair_key_matrix(key=''):
    key = clear_text(key).upper()
    key = key.replace('J','')
    unique = []
    matrix = []

    for each in key:
        if not unique.count(each):
            unique.append(each)
    
    for each in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
        if not unique.count(each):
            unique.append(each)
    
    for i in range(5):
        row = []
        for j in range(5):
            row.append(unique[i*5+j])
        matrix.append(row)

    return matrix

def find_position_matrix(matrix = [[]], value = ''):
    x = 0
    y = 0
    for i in range(len(matrix)):
        if matrix[i].count(value):
            x = i
            y = matrix[i].index(value)

    return [x, y]

def print_matrix(matrix = [[]]):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if j:
                print(' ', end='')
            print(matrix[i][j], end='')
        print()

def transpose_enc_dec(text, key, prev_key, opt):
    res = []
    if(opt == 0):
        diff = DIVIDE_SIZE - (len(key) % 5) 
        text += diff*'Z'
        # print(text)       
        temp = []
        # print(len(text)//DIVIDE_SIZE) 
        for i in range((len(text)//DIVIDE_SIZE)):
            temp.append( text[i*DIVIDE_SIZE:((i+1)*DIVIDE_SIZE)])
        # print(temp)
        for i in range(DIVIDE_SIZE):
            temp_str = ""
            for char in temp:
                temp_str += char[i]
            res.append(temp_str)
        return(''.join(res))
    else:
        mul = len(text)//DIVIDE_SIZE
        temp = []
        for i in range(DIVIDE_SIZE):
            temp.append(text[i*mul:((i+1)*mul)])
        # print(temp)
        for i in range(mul):
            temp_str = ""
            for char in temp:
                temp_str += char[i]
            res.append(temp_str)
        # print(key)
        # print(-(len(text)-len(prev_key)))
        # print(res)
        res_text = ''.join(res)
        final_res = res_text if (len(text)-len(prev_key) == 0) else res_text[:-(len(text)-len(prev_key))]
        return(final_res)    

def inverse_modulo(m, n):
    for i in range(n):
        if ( (m * i) % n == 1 ):
            return i
    return -1

def is_list_number(l=[]):
    for each in l:
        if not each.isdigit():
            return False
    return True

def hill_inverse_matrix(matrix=[[]]):
    inverse = [
        [
            (matrix[1][1] * matrix[2][2]) - (matrix[2][1] * matrix[1][2]),
            -((matrix[0][1] * matrix[2][2]) - (matrix[2][1] * matrix[0][2])),
            (matrix[0][1] * matrix[1][2]) - (matrix[1][1] * matrix[0][2])
        ],
        [
            -((matrix[1][0] * matrix[2][2]) - (matrix[2][0] * matrix[1][2])),
            (matrix[0][0] * matrix[2][2]) - (matrix[2][0] * matrix[0][2]),
            -((matrix[0][0] * matrix[1][2]) - (matrix[1][0] * matrix[0][2]))
        ],
        [
            (matrix[1][0] * matrix[2][1]) - (matrix[2][0] * matrix[1][1]),
            -((matrix[0][0] * matrix[2][1]) - (matrix[2][0] * matrix[0][1])),
            (matrix[0][0] * matrix[1][1]) - (matrix[1][0] * matrix[0][1])
        ]
    ]
    
    det = (matrix[0][0] * inverse[0][0] + matrix[0][1] * inverse[1][0] + matrix[0][2] * inverse[2][0]) % 26

    if det == 0:
        return False
    
    det_inverse = inverse_modulo(det,26)

    if det_inverse == -1:
        return False

    for i in range(3):
        for j in range(3):
            inverse[i][j] = (inverse[i][j] * det_inverse) % 26

    return inverse

def hill_key_matrix(key=[]):
    key = list(map(int,key))
    matrix = []

    for i in range(3):
        row = []
        for j in range(3):
            row.append(key[i*3+j])
        matrix.append(row)

    return matrix

def hill_matrix_dot(matrix=[[]], row=[]):
    result = [0, 0, 0]

    for i in range(3):
        result[i] += matrix[i][0] * row[0] + matrix[i][1] * row[1] + matrix[i][2] * row[2]

    return result

def generate_auto_key(text, key):
    new_key = key + text[:(len(text)-len(key))]
    return new_key

def load_binary(filename):
    text = ""
    with open (filename, 'rb') as files:
        byte = files.read()
        text = byte.decode('iso8859-1')
    return text

def save_binary(filename, text):
    with open (filename, 'wb') as files:
        files.write(text.encode('iso8859-1'))

class Crypto():
    @staticmethod
    def playfair_encrypt(plaintext, key):
        matrix = playfair_key_matrix(key)
        plaintext = clear_text(plaintext).upper()
        plaintext = plaintext.replace('J','I')
        bigram = []
        cipher = ''
        
        while plaintext:
            if len(plaintext) == 1:
                bigram.append(plaintext + 'X')
                plaintext = ''
            elif plaintext[0] == plaintext[1]:
                bigram.append(plaintext[0] + 'X')
                plaintext = plaintext[1:]
            else:
                bigram.append(plaintext[0:2])
                plaintext = plaintext[2:]
        
        for each in bigram:
            loc_first = find_position_matrix(matrix,each[0])
            loc_second = find_position_matrix(matrix,each[1])
            
            # RULES
            if loc_first[0] == loc_second[0]:
                if loc_first[1] == 4:
                    cipher += matrix[loc_first[0]][0]
                else:
                    cipher += matrix[loc_first[0]][loc_first[1]+1]

                if loc_second[1] == 4:
                    cipher += matrix[loc_second[0]][0]
                else:
                    cipher += matrix[loc_second[0]][loc_second[1]+1]
            elif loc_first[1] == loc_second[1]:
                if loc_first[0] == 4:
                    cipher += matrix[0][loc_first[1]]
                else:
                    cipher += matrix[loc_first[0]+1][loc_first[1]]

                if loc_second[0] == 4:
                    cipher += matrix[0][loc_second[1]]
                else:
                    cipher += matrix[loc_second[0]+1][loc_second[1]]
            else:
                cipher += matrix[loc_first[0]][loc_second[1]]
                cipher += matrix[loc_second[0]][loc_first[1]]
        
        return cipher

    @staticmethod
    def playfair_decrypt(ciphertext, key):
        matrix = playfair_key_matrix(key)
        ciphertext = clear_text(ciphertext).upper()
        ciphertext = split_text(ciphertext,2)
        plainlist = []
        plaintext = ''
        
        for each in ciphertext:
            bigram = ''
            loc_first = find_position_matrix(matrix,each[0])
            loc_second = find_position_matrix(matrix,each[1])
            
            # RULES
            if loc_first[0] == loc_second[0]:
                if loc_first[1] == 0:
                    bigram += matrix[loc_first[0]][4]
                else:
                    bigram += matrix[loc_first[0]][loc_first[1]-1]

                if loc_second[1] == 0:
                    bigram += matrix[loc_second[0]][4]
                else:
                    bigram += matrix[loc_second[0]][loc_second[1]-1]
            elif loc_first[1] == loc_second[1]:
                if loc_first[0] == 0:
                    bigram += matrix[4][loc_first[1]]
                else:
                    bigram += matrix[loc_first[0]-1][loc_first[1]]

                if loc_second[0] == 0:
                    bigram += matrix[4][loc_second[1]]
                else:
                    bigram += matrix[loc_second[0]-1][loc_second[1]]
            else:
                bigram += matrix[loc_first[0]][loc_second[1]]
                bigram += matrix[loc_second[0]][loc_first[1]]

            plainlist.append(bigram)
            
        plainlist.reverse()
        removed = 0

        for each in plainlist:
            if plaintext:
                if each[0] == plaintext[0] and each[1] == 'X':
                    plaintext = each[0] + plaintext
                    removed += 1
                else:
                    plaintext = each + plaintext
            else:
                plaintext = each + plaintext
        
        if (len(plaintext)+removed) % 2 == 0:
            plaintext = plaintext[:-1]
        
        return plaintext

    @staticmethod
    def hill_encrypt(plaintext, key):
        plaintext = clear_text(plaintext).upper()
        if len(plaintext) % 3 != 0:
            return 'CAN\'T ENCRYPT, PLAIN TEXT\'S LENGTH IS NOT MULTIPLIER OF 3'

        key = key.split(' ')
        if len(key) != 9 or not is_list_number(key):
            return 'CAN\'T ENCRYPT, KEY MUST BE 9 NUMBER SEPERATED BY SPACE'

        matrix = hill_key_matrix(key)
        plaintext = split_text(plaintext,3)
        ciphertext = ''

        for each in plaintext:
            each_num = [
                alpha_to_num(each[0]),
                alpha_to_num(each[1]),
                alpha_to_num(each[2])
            ]

            result = hill_matrix_dot(matrix,each_num)
            ciphertext += num_to_alpha(result[0]%26)
            ciphertext += num_to_alpha(result[1]%26)
            ciphertext += num_to_alpha(result[2]%26)

        return ciphertext

    @staticmethod
    def hill_decrypt(ciphertext, key):
        ciphertext = clear_text(ciphertext).upper()
        if len(ciphertext) % 3 != 0:
            return 'CAN\'T DECRYPT, CIPHERTEXT\'S LENGTH IS NOT MULTIPLIER OF 3'

        key = key.split(' ')
        if len(key) != 9 or not is_list_number(key):
            return 'CAN\'T DECRYPT, KEY MUST BE 9 NUMBER SEPERATED BY SPACE'
        
        matrix = hill_key_matrix(key)
        matrix = hill_inverse_matrix(matrix)
        if matrix==False:
            return 'CAN\'T DECRYPT, WRONG KEY'

        ciphertext = split_text(ciphertext,3)
        plaintext = ''

        for each in ciphertext:
            each_num = [
                alpha_to_num(each[0]),
                alpha_to_num(each[1]),
                alpha_to_num(each[2])
            ]

            result = hill_matrix_dot(matrix,each_num)
            plaintext += num_to_alpha(result[0]%26)
            plaintext += num_to_alpha(result[1]%26)
            plaintext += num_to_alpha(result[2]%26)

        return plaintext
    
    @staticmethod
    def string_add_seperator(text, n=5, sep=' '):
        result = ''
        first = True

        while text:
            if not first: result += sep
            else: first = False

            result += text[:n]
            text = text[n:]

        return result

    @staticmethod
    def vigenere_standard(text, key, opt):
        temp_text = clear_text(text).upper()
        new_key = generate_key_repeat(text, key).upper()
        new_text = ""

        # opt = 0 --> encrypt, opt = 1 --> decrypt
        if(opt == 0):
            for char, key in zip(temp_text, new_key):
                new_text += chr(65 + (ord(char)+ord(key)) % 26)
        else:
            for char, key in zip(temp_text, new_key):
                new_text += chr(65 + (ord(char)-ord(key)) % 26)
            new_text = new_text.lower()
        return new_text

    @staticmethod
    def vigenere_full(text, key, opt):
        temp_text = clear_text(text).upper()
        new_key = generate_key_repeat(temp_text, key).upper()
        new_text = ""
        # print(temp_text)
        if(opt == 0):
            keys = generate_full_vigenere_key()
            temp = []
            for item in keys:
                temp_str = "".join(item)
                temp.append(temp_str)

            rows = ""
            for char, temp_key in zip(temp_text, new_key):
                print(ord(temp_key)-65, ord(char)-65)
                rows+= str(ord(temp_key)-65) + ";"
                new_text += keys[ord(temp_key)-65][ord(char)-65]
            print(rows)
            print(new_text)
            save_file('keystore.txt', rows + "," + ''.join(temp))
        else:
            temp = load_plain_text('keystore.txt').split(",")
            keys = split_text(temp[1], 26)
            key_rows = temp[0].split(";")[0:-1]
            # print(key_rows)
            # print(keys)
            for char, temp_key in zip(temp_text, key_rows):
                # print(keys[int(temp_key)])
                idx = keys[int(temp_key)].index(char)
                new_text += chr(idx+65)
            print(new_text.lower())
        return new_text

    @staticmethod
    def super_encrypt(text, key, opt):
        res = ""
        if(opt == 0):
            temp_text = clear_text(text).upper()
            new_key = generate_key_repeat(temp_text, key).upper()
            # print(new_key)
            save_file('temp_keystore.txt', new_key)
            temp = Crypto().vigenere_standard(text, key, opt) 
            res = transpose_enc_dec(temp,new_key, new_key, opt)
        else:
            temp_text = clear_text(text).upper()
            new_key = generate_key_repeat(temp_text, key).upper()
            prev_key = load_plain_text('temp_keystore.txt')
            print(prev_key)
            temp_res = transpose_enc_dec(temp_text, new_key, prev_key, opt)
            res = Crypto().vigenere_standard(temp_res, key, opt)
        return res

    @staticmethod
    def affine_cipher(text, key, opt):
        res = ""
        text = text.upper()
        # print(text)
        keys = key.split(" ")
        if(opt == 0):
            for i in range(len(text)):
                if(text[i] != ' '):
                    res += chr(65 + ((ord(text[i])-65) * int(keys[0]) + int(keys[1])) % 26)
                else:
                    res += ' '
        else:
            inv = inverse_modulo(int(keys[0]), 26)
            # print(inv)
            for i in range(len(text)):
                # print(inv, ord(text[i])-65, keys[1], (inv * (ord(text[i])-65 - int(keys[1]))))
                if(text[i] != ' '):
                    res += chr(65 + (inv * (ord(text[i])-65 - int(keys[1]))) % 26)
                else:
                    res += ' '

        return res.lower()

    @staticmethod
    def auto_key_vigenere(text, key, opt):
        text = clear_text(text).upper()
        new_text = ""

        # opt = 0 --> encrypt, opt = 1 --> decrypt
        if(opt == 0):
            new_key = generate_auto_key(text, key)
            for char, key in zip(text, new_key):
                new_text += chr(65 + (ord(char)+ord(key)) % 26)
            save_file('temp_key.txt', new_key)
        else:
            new_key = load_plain_text('temp_key.txt')
            for char, key in zip(text, new_key):
                new_text += chr(65 + (ord(char)-ord(key)) % 26)
            new_text = new_text.lower()
        return new_text

    @staticmethod
    def extended_vigenere_encrypt(filename, key):
        temp_text = load_binary(filename)
        new_key = generate_key_repeat(temp_text, key)
        new_text = ""
        
        for char, key in zip(temp_text, new_key):
            new_text += ( chr((ord(char)+ord(key)) % 256) )
        save_file('temp_key.txt', new_key)
        save_file_name = filename.split('.')
        save_file_name = save_file_name[0] + '_encrypt.' + save_file_name[1]
        save_binary(save_file_name, new_text)

    @staticmethod
    def extended_vigenere_decrypt(filename, key):
        temp_text = load_binary(filename)
        new_key = load_plain_text('temp_key.txt')
        new_text = ""

        for char, key in zip(temp_text, new_key):
            new_text += ( chr((ord(char)-ord(key)) % 256) )

        save_file_name = filename.split('.')
        save_file_name = save_file_name[0] + '_decrypt.' + save_file_name[1]
        save_binary(save_file_name, new_text)





if __name__ == "__main__":
    # temp = load_plain_text("README.md")
    # print(temp)

    # extended_vigenere_encrypt('Tucil-1-Sem1-2020-2021.pdf', 'temp')
    # extended_vigenere_decrypt('Tucil-1-Sem1-2020-2021.pdf', 'temp')
    # print(vigenere_standard("thisplaintext", "sonysonysonys", 0))
    # print(generate_key_repeat("testtests", "test"))
    # print(generate_full_vigenere_key())
    # vigenere_full("OXAU", "temp", 1)
    # print(super_encrypt("MIIEEIIMMZ", "temp", 1))
    # print(Crypto().affine_cipher("hkzo oxo oxfkh","7 10",1))
    pass
