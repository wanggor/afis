import base64

def encode(key, string):
    string = string.lower()
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) + ord(key_c)) % 36)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string

def decode(key, string):
    # string = string.lower()
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) - ord(key_c) % 36)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string

key = "aa"
encrypt_text = encode(key,"hello")
print(encrypt_text)
decode_text = decode(key, encrypt_text)
print(decode_text)

print(ord("a"))