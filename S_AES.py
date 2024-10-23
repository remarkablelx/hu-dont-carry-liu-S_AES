import random
import secrets
import time

from PyQt5.QtWidgets import QDesktopWidget

State_BOX = [0xA, 0x4, 0x7, 0x9]
S_BOX = [0x9, 0x4, 0xA, 0xB, 0xD, 0x1, 0x8, 0x5, 0x6, 0x2, 0x0, 0x3, 0xC, 0xE, 0xF, 0x7]
InvS_BOX = [0xA, 0x5, 0x9, 0xB, 0x1, 0x7, 0x8, 0xF, 0x6, 0x0, 0x2, 0x3, 0xC, 0x4, 0xD, 0xE]
Cfs_BOX = [0x1, 0x4, 0x4, 0x1]
InvCfs_BOX = [0x9, 0x2, 0x2, 0x9]
Polynomial = 0b10011
RCON_1 = 0b10000000
RCON_2 = 0b00110000


# 将二进制字符串转换为整数
def bin_str_to_int(bin_str):
    return int(bin_str, 2)


# 将整数转换为二进制字符串
def int_to_bin_str(value, bits=16):
    return bin(value)[2:].zfill(bits)


# 密钥加
def key_plus(input, key):
    input_int = bin_str_to_int(input)
    key_int = bin_str_to_int(key)
    result = input_int ^ key_int
    return int_to_bin_str(result)


# 半字节替换
def substitute_half_bytes(input, box):
    input_int = bin_str_to_int(input)
    substituted_value = 0
    for i in range(4):
        half_byte = (input_int >> (i * 4)) & 0xF
        substituted_half_byte = box[half_byte]
        substituted_value |= substituted_half_byte << (i * 4)
    return int_to_bin_str(substituted_value)


# 行移位
def row_shift(input):
    input_int = bin_str_to_int(input)
    half_byte = [0] * 4
    for i in range(4):
        half_byte[i] = (input_int >> (i * 4)) & 0xF
    row_value = (half_byte[3] << 12) | (half_byte[0] << 8) | (half_byte[1] << 4) | half_byte[2]
    return int_to_bin_str(row_value)


# 伽罗华域加法
def GF_addition(a, b):
    result = a ^ b
    return result


# 伽罗华域乘法
def GF_multiplication(a, b):
    result = 0
    for i in range(4):
        if (b & (1 << i)) != 0:
            result ^= a << i
    for i in range(7, 3, -1):
        if (result & (1 << i)) != 0:
            result ^= Polynomial << (i - 4)
    return result & 0xF


# 列混淆
def col_confusion(input, box):
    input_int = bin_str_to_int(input)
    half_byte = [0] * 4
    for i in range(4):
        half_byte[i] = (input_int >> (i * 4)) & 0xF
    s11 = GF_addition(GF_multiplication(box[0], half_byte[3]), GF_multiplication(box[1], half_byte[2]))
    s21 = GF_addition(GF_multiplication(box[2], half_byte[3]), GF_multiplication(box[3], half_byte[2]))
    s12 = GF_addition(GF_multiplication(box[0], half_byte[1]), GF_multiplication(box[1], half_byte[0]))
    s22 = GF_addition(GF_multiplication(box[2], half_byte[1]), GF_multiplication(box[3], half_byte[0]))
    col_value = (s11 << 12) | (s21 << 8) | (s12 << 4) | s22
    return int_to_bin_str(col_value)


# 密钥扩展
def key_expansion(key):
    key_int = bin_str_to_int(key)
    half_byte = [0] * 4
    for i in range(4):
        half_byte[3 - i] = (key_int >> (i * 4)) & 0xF
    w0 = (half_byte[0] << 4) | half_byte[1]
    w1 = (half_byte[2] << 4) | half_byte[3]
    SubNib1 = (S_BOX[half_byte[3]] << 4) | S_BOX[half_byte[2]]
    w2 = w0 ^ RCON_1 ^ SubNib1
    w3 = w1 ^ w2
    half_byte = [0] * 2
    for i in range(2):
        half_byte[1 - i] = (w3 >> (i * 4)) & 0xF
    SubNib2 = (S_BOX[half_byte[1]] << 4) | S_BOX[half_byte[0]]
    w4 = w2 ^ RCON_2 ^ SubNib2
    w5 = w3 ^ w4

    key_schedule = []
    key_schedule.append(int_to_bin_str((w0 << 8) | w1))
    key_schedule.append(int_to_bin_str((w2 << 8) | w3))
    key_schedule.append(int_to_bin_str((w4 << 8) | w5))

    return key_schedule


# 加密
def encrypt(input, key):
    key_expanded = key_expansion(key)
    result1 = key_plus(input, key_expanded[0])
    result2 = substitute_half_bytes(result1, S_BOX)
    result3 = row_shift(result2)
    result4 = col_confusion(result3, Cfs_BOX)
    result5 = key_plus(result4, key_expanded[1])
    result6 = substitute_half_bytes(result5, S_BOX)
    result7 = row_shift(result6)
    result8 = key_plus(result7, key_expanded[2])
    return result8


# 解密
def decrypt(input, key):
    key_expanded = key_expansion(key)
    result1 = key_plus(input, key_expanded[2])
    result2 = row_shift(result1)
    result3 = substitute_half_bytes(result2, InvS_BOX)
    result4 = key_plus(result3, key_expanded[1])
    result5 = col_confusion(result4, InvCfs_BOX)
    result6 = row_shift(result5)
    result7 = substitute_half_bytes(result6, InvS_BOX)
    result8 = key_plus(result7, key_expanded[0])
    return result8


# 加密ASCII字符串
def encrypt_ASCII(input, key):
    if not all(0 <= ord(c) < 255 for c in input):
        raise ValueError("输入包含非ASCII字符")
    binary_input = string_to_bin(input)
    binary_chunks = [binary_input[i:i + 16] for i in range(0, len(binary_input), 16)]
    encrypted_chunks = []
    for chunk in binary_chunks:
        if len(chunk) != 16:
            raise ValueError("输入必须为偶数个ASCII字符")
        encrypted_chunk = encrypt(chunk, key)
        encrypted_chunks.append(encrypted_chunk)
    encrypted_binary = ''.join(encrypted_chunks)
    encrypted_ascii = bin_to_string(encrypted_binary)
    return encrypted_ascii


# 解密ASCII字符串
def decrypt_ASCII(encrypted_str, key):
    encrypted_binary = string_to_bin(encrypted_str)
    binary_chunks = [encrypted_binary[i:i + 16] for i in range(0, len(encrypted_binary), 16)]
    decrypted_chunks = []
    for chunk in binary_chunks:
        decrypted_chunk = decrypt(chunk, key)
        decrypted_chunks.append(decrypted_chunk)
    decrypted_binary = ''.join(decrypted_chunks)
    decrypted_ascii = bin_to_string(decrypted_binary)
    return decrypted_ascii


# ASCII字符转换位二进制数
def string_to_bin(input):
    return ''.join(f'{ord(char):08b}' for char in input)


# 二进制数转换为ASCII字符
def bin_to_string(binary_str):
    chars = [chr(int(binary_str[i:i + 8], 2)) for i in range(0, len(binary_str), 8)]
    return ''.join(chars)


# 双重加密(K1 != K2)
def encrypt_double(input, key):
    key1 = key[:16]
    key2 = key[16:]
    midtext = encrypt(input, key1)
    output = decrypt(midtext, key2)
    return output


# 双重解密(K1 != K2)
def decrypt_double(input, key):
    key1 = key[:16]
    key2 = key[16:]
    midtext = encrypt(input, key2)
    output = decrypt(midtext, key1)
    return output


# 中间相遇攻击
def middle_attack(inputs, outputs):
    start_time = time.time()
    found_keys = []
    possible_keys = None
    for idx in range(len(inputs)):
        input_bin = inputs[idx]
        output_bin = outputs[idx]
        encrypt_dict = {}
        decrypt_dict = {}
        for K1 in range(0x0000, 0xFFFF + 1):
            K1_str = bin(K1)[2:].zfill(16)
            midtext1 = encrypt(input_bin, K1_str)
            encrypt_dict[midtext1] = K1_str
        for K2 in range(0x0000, 0xFFFF + 1):
            K2_str = bin(K2)[2:].zfill(16)
            midtext2 = encrypt(output_bin, K2_str)
            decrypt_dict[midtext2] = K2_str
        current_matches = [(encrypt_dict[m], decrypt_dict[m]) for m in encrypt_dict if m in decrypt_dict]
        if possible_keys is None:
            possible_keys = set(current_matches)
        else:
            possible_keys.intersection_update(current_matches)
    end_time = time.time()
    if possible_keys and len(possible_keys) > 0:
        for K1_str, K2_str in possible_keys:
            key = K1_str + K2_str
            found_keys.append(key)
        print(f"找到 {len(possible_keys)} 组匹配的密钥对:")
    else:
        print("未找到匹配的密钥对")
    elapsed_time = end_time - start_time
    print(f"算法执行时间: {elapsed_time:.6f} 秒")
    return found_keys, elapsed_time


# 三重加密
def encrypt_triple(input, key):
    key1 = key[:16]
    key2 = key[16:32]
    key3 = key[32:]
    midtext1 = encrypt(input, key1)
    midtext2 = decrypt(midtext1, key2)
    output = encrypt(midtext2, key3)
    return output


# 三重解密
def decrypt_triple(input, key):
    key1 = key[:16]
    key2 = key[16:32]
    key3 = key[32:]
    midtext2 = decrypt(input, key3)
    midtext1 = encrypt(midtext2, key2)
    output = decrypt(midtext1, key1)
    return output


# 初始向量(IV)的生成
def generate_iv():
    return bin(random.randint(0x0000, 0xFFFF))[2:].zfill(16)


# 检查输入类型并进行处理
def preprocess_input(input_data, input_type):
    if input_type == 'binary':
        if not all(c in '01' for c in input_data):
            raise ValueError("输入必须是合法的二进制字符串。")
        if len(input_data) % 16 != 0:
            raise ValueError("二进制输入的长度必须是16的倍数。")
        return [input_data[i:i+16] for i in range(0, len(input_data), 16)]

    elif input_type == 'ascii':
        if len(input_data) % 2 != 0:
            raise ValueError("ASCII 输入必须是偶数个字符。")
        for char in input_data:
            if ord(char) > 0xFF:
                raise ValueError("所有字符必须是合法的 ASCII 字符。")
        binary_data = ''.join([bin(ord(char))[2:].zfill(8) for char in input_data])
        return [binary_data[i:i+16] for i in range(0, len(binary_data), 16)]

    elif input_type == 'unicode':
        return [bin(ord(c))[2:].zfill(16) for c in input_data]

    else:
        raise ValueError("不支持的输入类型。")


# 将二进制字符串转换为ASCII字符
def binary_to_ascii(binary_str):
    if len(binary_str) % 8 != 0:
        raise ValueError("二进制字符串的长度必须是8的倍数。")
    ascii_output = ''.join([chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)])
    return ascii_output


# 将二进制字符串转换为Unicode字符
def binary_to_unicode(binary_str):
    if len(binary_str) % 16 != 0:
        raise ValueError("二进制字符串的长度必须是16的倍数。")
    unicode_output = ''.join([chr(int(binary_str[i:i+16], 2)) for i in range(0, len(binary_str), 16)])
    return unicode_output


# CBC模式加密
def encrypt_CBC(plaintext, key, iv, input_type):
    blocks = preprocess_input(plaintext, input_type)
    ciphertext = []
    previous_block = int(iv, 2)
    for block in blocks:
        block_int = int(block, 2)
        xor_result = block_int ^ previous_block
        encrypted_block = encrypt(bin(xor_result)[2:].zfill(16), key)
        ciphertext.append(encrypted_block)
        previous_block = int(encrypted_block, 2)

    if input_type == 'binary':
        return ''.join(ciphertext)
    elif input_type == 'ascii':
        binary_str = ''.join(ciphertext)
        return binary_to_ascii(binary_str)
    elif input_type == 'unicode':
        binary_str = ''.join(ciphertext)
        return binary_to_unicode(binary_str)
    else:
        raise ValueError("不支持的输入类型。")


# CBC模式解密
def decrypt_CBC(ciphertext, key, iv, input_type):
    if input_type == 'binary':
        blocks = [ciphertext[i:i + 16] for i in range(0, len(ciphertext), 16)]
    elif input_type == 'ascii':
        binary_data = ''.join([bin(ord(char))[2:].zfill(8) for char in ciphertext])
        blocks = [binary_data[i:i + 16] for i in range(0, len(binary_data), 16)]
    elif input_type == 'unicode':
        binary_data = ''.join([bin(ord(char))[2:].zfill(16) for char in ciphertext])
        blocks = [binary_data[i:i + 16] for i in range(0, len(binary_data), 16)]
    else:
        raise ValueError("不支持的输入类型。")

    plaintext = []
    previous_block = int(iv, 2)

    for encrypted_block in blocks:
        encrypted_int = int(encrypted_block, 2)
        decrypted_block = decrypt(bin(encrypted_int)[2:].zfill(16), key)
        original_block = int(decrypted_block, 2) ^ previous_block
        plaintext.append(bin(original_block)[2:].zfill(16))
        previous_block = encrypted_int

    if input_type == 'binary':
        return ''.join(plaintext)
    elif input_type == 'ascii':
        binary_str = ''.join(plaintext)
        return binary_to_ascii(binary_str)
    elif input_type == 'unicode':
        binary_str = ''.join(plaintext)
        return binary_to_unicode(binary_str)
    else:
        raise ValueError("不支持的输入类型。")


# 获取密钥函数
def generate_key(input):
    length = int(input)
    key = secrets.randbits(length)
    key_bin = bin(key).replace('0b', '').zfill(length)
    return key_bin


# 居中页面函数
def center(self):
    screen = QDesktopWidget().screenGeometry()
    size = self.geometry()
    x = (screen.width() - size.width()) // 2
    y = (screen.height() - size.height()) // 2
    self.move(x, y)