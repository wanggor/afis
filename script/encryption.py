import base64

char = "abcdefghijklmnopqrstuvwxyz0123456789"

def encode(key, string):
    if len(key) != 0:
        string = string.lower()
        encoded_chars = []
        for i in range(len(string)):
            if string[i] in char:
                key_c = key[i % len(key)]
                encoded_c = char[(char.index(string[i]) + char.index(key_c)) % len(char)]
                encoded_chars.append(encoded_c)
            else:
                encoded_chars.append(" ")
        encoded_string = "".join(encoded_chars)
        return encoded_string
    else:
        return string

def decode(key, string):
    if len(key) != 0:
        encoded_chars = []
        for i in range(len(string)):
            if string[i] in char:
                key_c = key[i % len(key)]
                encoded_c = char[(char.index(string[i]) - char.index(key_c)) % len(char)]
                encoded_chars.append(encoded_c)
            else:
                encoded_chars.append(" ")
        encoded_string = "".join(encoded_chars)
        return encoded_string
    else:
        return string

if __name__ == "__main__":
    key = "112"
    msg = "hed;llo;"
    encrypt_text = encode(key,msg)
    print(encrypt_text)
    # encrypt_text = "85dcf a"
    decode_text = decode(key, encrypt_text)
    print(decode_text)