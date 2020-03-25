from cs50 import get_int


def main():
    # Ask the user for height between 1 - 8
    while True:
        height = get_int("Height: ")
        if height > 0 and height < 9:
            break

    draw_pyramid(height)


# Print n number of spaces
def print_space(n):
    for i in range(n):
        print(" ", end="")

# Print n number of hashes


def print_hash(n):
    for i in range(n):
        print("#", end="")


# Draw the rows of the pyramid
def draw_pyramid(n):
    # Where n is the height, will print number of rows equal to the height
    for i in range(1, (n+1)):
        print_space(n - i)
        print_hash(i)
        print_space(2)
        print_hash(i)
        print("")


if __name__ == "__main__":
    main()