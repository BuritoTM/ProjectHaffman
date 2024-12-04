import heapq
from collections import defaultdict


class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(frequency):
    priority_queue = []
    for char, freq in frequency.items():
        heapq.heappush(priority_queue, Node(char, freq))

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return priority_queue[0]


def generate_codes(node, prefix='', codebook={}):
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        generate_codes(node.left, prefix + '0', codebook)
        generate_codes(node.right, prefix + '1', codebook)
    return codebook


def encode(text, codebook):
    return ''.join(codebook[char] for char in text)


def write_to_binary_file(encoded_text, frequency, filename):
    byte_array = bytearray()

    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        if len(byte) < 8:
            byte += '0' * (8 - len(byte))
        byte_array.append(int(byte, 2))

    with open(filename, 'wb') as f:
        # Сохраняем частоты в строку через пробел
        freq_string = ' '.join([f"{char}:{freq}" for char, freq in frequency.items()])
        f.write(freq_string.encode('utf-8'))
        f.write(b"\n")  # Пустая строка, чтобы отделить частоты от закодированного текста
        f.write(byte_array)


def read_from_binary_file(filename):
    with open(filename, 'rb') as f:
        frequency = {}
        line = f.readline()
        # Разделяем по пробелам
        freq_data = line.decode('utf-8').strip().split(' ')

        for item in freq_data:
            if ':' in item:  # Проверка на наличие двоеточия
                char, freq = item.split(':')  

                if char == '':
                    char = ' '

                frequency[char] = int(freq)  # Записываем частоту

        encoded_text = ''.join(format(byte, '08b') for byte in f.read())

    return frequency, encoded_text


def decode(encoded_text, root):
    decoded_output = ""
    current_node = root
    for bit in encoded_text:
        current_node = current_node.left if bit == '0' else current_node.right
        if current_node.char is not None:
            decoded_output += current_node.char  
            current_node = root
    return decoded_output


def print_huffman_tree(node, prefix=''):
    if node is not None:
        if node.char is not None:
            print(f"{prefix}* {node.char} (freq: {node.freq})")
        else:
            print(f"{prefix}* (freq: {node.freq})")
        print_huffman_tree(node.left, prefix + '  ')
        print_huffman_tree(node.right, prefix + '  ')


def main(input_filename, output_filename):
    action = input("Вы хотите закодировать или декодировать текст? (введите 'encode' или 'decode'): ").strip().lower()

    if action == 'encode':
        with open(input_filename, 'r', encoding='utf-8') as file:
            text = file.read()

        frequency = defaultdict(int)
        for char in text:
            frequency[char] += 1

        huffman_tree = build_huffman_tree(frequency)
        print("\nДерево Хаффмана:")
        print_huffman_tree(huffman_tree)

        huffman_codes = generate_codes(huffman_tree)
        encoded_text = encode(text, huffman_codes)
        write_to_binary_file(encoded_text, frequency, output_filename)

        print("\nТаблица кодов Хаффмана:")
        for char, code in huffman_codes.items():
            print(f"'{char}': {code}")

        original_size = len(text)
        encoded_size = len(encoded_text) // 8 + (1 if len(encoded_text) % 8 else 0)
        print("\nРазмер исходного текста:", original_size, "байт")
        print("Размер закодированного текста:", encoded_size, "байт")

        print("\nОригинальная строка в двоичном виде:")
        original_binary = ''.join(format(ord(char), '08b') for char in text)
        print(original_binary)

        print("\nЗакодированный текст в двоичном виде:")
        print(encoded_text)

    elif action == 'decode':
        frequency, encoded_text = read_from_binary_file(output_filename)
        huffman_tree = build_huffman_tree(frequency)
        decoded_text = decode(encoded_text, huffman_tree)

        print("\nДекодированный текст:")
        print(decoded_text)

    else:
        print("Неверный выбор. Пожалуйста, введите 'encode' или 'decode'.")

input_filename = 'input.txt'  
output_filename = 'output.bin' 
main(input_filename, output_filename)
