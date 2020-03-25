import sys
from cs50 import get_string


def main():
    # Test if the user has only input two strings (the name of the program and the keyword)
    if len(sys.argv) != 2:
        print("Usage: ./vigenere keyword")
        sys.exit(1)

    # Test if the keyword is strictly alphabetic
    if not sys.argv[1].isalpha():
        print("Usage: ./vigenere keyword")
        sys.exit(1)

    # Ask the user to input plaintext
    text = get_string("plaintext: ")

    # Set numeric value of each keyword letter
    # Adjust the default number given by ASCII table
    # Once done a = 0, b = 1, c = 2, etc.
    # Uppercase letters will have same value as lc
    key = []
    for i in range(len(sys.argv[1])):
        if sys.argv[1][i].islower():
            key.append(ord(sys.argv[1][i]) - ord('a'))
        elif sys.argv[1][i].isupper():
            key.append(ord(sys.argv[1][i]) - ord('A'))

    # Shift each alphabetic character in the plaintext
    cipher = []
    key_counter = 0
    for i in range(len(text)):
        if text[i].isalpha():
            cipher.append(shift(text[i], key[key_counter]))
            key_counter += 1
            if key_counter == len(sys.argv[1]):
                key_counter = 0
        else:
            cipher.append(text[i])

    # Join the elements of the cipher list into a str
    cipher_str = "".join(cipher)

    # Print out the ciphertext where key has been applied
    print("ciphertext: ", cipher_str)

# Apply key to each alphabetic value in the ciphertext array


def shift(text, key):
    # Check if the values are alphabetic
    # If the values are alphabetic, apply the key
    cipher = ""

    # Test if, once key applied, character is lowercase and would exceed z on ASCII
    # If so, subtract 26 (# of chars in alphabet to functionally loop around)
    if text.islower() and (ord(text) + key) > ord('z'):
        cipher = cipher + chr(ord(text) + key - 26)

    # Test if, once key applied, character is uppercase and would exceed Z on ASCII
    # If so, subtract 26 (# of chars in alphabet to functionally loop around)
    elif text.isupper() and (ord(text) + key) > ord('Z'):
        cipher = cipher + (chr(ord(text) + key - 26))

    # If we don't need to deal with those situations
    # simply apply the key

    else:
        cipher = cipher + (chr(ord(text) + key))

    return cipher


if __name__ == "__main__":
    main()