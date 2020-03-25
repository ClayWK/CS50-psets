from cs50 import get_string
from sys import argv


def main():
    # Test if the user has only input two strings (the name of the program and a dictionary)
    if len(argv) != 2:
        print("Usage: python bleep.py dictionary")
        exit(1)

    # open dictionary in read mode
    f = open(argv[1], 'r')

    # create an empty set
    banned_words = set()

    # iterate over every line in dictionary
    # add each word in dictionary in the set
    for line in f:
        banned_words.add(line.rstrip())

    # Ask the user to input a message
    message = get_string("What message would you like to censor: ")

    message_tokens = message.split()
    censored_tokens = []
    for token in message_tokens:
        if token.lower() in banned_words:
            censored_tokens.append("*" * len(token))
        else:
            censored_tokens.append(token)

    censored_message = " ".join(censored_tokens)
    print(censored_message)

    # close dictionary
    f.close


if __name__ == "__main__":
    main()
