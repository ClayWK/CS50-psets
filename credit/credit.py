from cs50 import get_int


def main():
    # Ask the user for card number with 13, 15 or 16 digits
    card_number = get_int("Number: ")

    # Convert the integer input by the user into a list of strings
    nums = list(map(int, str(card_number)))

    # Determine the length of the card number input by user
    card_length = len(nums)

    # If card length is not 13, 14 or 16 digits, card is invalid
    if card_length < 13 or card_length == 14 or card_length > 16:
        print("INVALID")
    else:
        # Pull out every other digit in the card, starting with the second to last digit
        # Multiply the extracted digits by 2
        every_other_nums = extract_every_other(nums)
        double_every_other = [i * 2 for i in every_other_nums]

        # Split out any numbers in the array that are >= 10 into two separate digits
        double_every_other = single_digits(double_every_other)

        # Calculate the sum of the digits in the every_other_array
        check_sum = sum(double_every_other)

        # Calculate sum of the remaining digits, add to sum of digits above
        remaining_nums = remaining_digits(nums)
        check_sum = check_sum + sum(remaining_nums)

        # Test if card follows VISA requirements
        if (check_sum % 10 == 0 and card_length == 13) or (card_length == 16 and nums[0] == 4):
            print("VISA")

        # Test if card follows AMEX requirements
        elif check_sum % 10 == 0 and card_length == 15 and nums[0] == 3 and (nums[1] == 4 or nums[1] == 7):
            print("AMEX")

        # Test if card follows MASTERCARD requirements
        elif check_sum % 10 == 0 and card_length == 16 and nums[0] == 5 and (nums[1] == 1 or nums[1] == 2 or nums[1] == 3 or nums[1] == 4 or nums[1] == 5):
            print("MASTERCARD")

        # Otherwise, card is invalid
        else:
            print("INVALID")

# Extracts every pther digit starting with second to last digit


def extract_every_other(array):
    n = len(array)
    if n % 2 == 0:
        every_other_nums = array[0::2]
        return every_other_nums
    if n % 2 != 0:
        every_other_nums = array[1::2]
        return every_other_nums


# If any numbers in the list are more than a single digit, separate out the digits
# This function only works for numbers between 10 - 99, but our numbers can never exceed 18
# Function looks through the array and applies modular arithmetic to any number > 10
# For numbers > 10 the modulo is moved into a cell later in the list
def single_digits(array):
    for i in range(len(array)):
        if array[i] >= 10:
            x = array[i]
            y = array[i]
            x = x % 10
            array[i] = (y // 10)
            array.append(x)
    return array

# Extracts digits that weren't previously extracted
# Extracts every other digit based off of the lst digit in the card number
# Takes an an input card_length, int_array and x, which should be 0


def remaining_digits(array):
    n = len(array)
    if n % 2 == 0:
        remaining_nums = array[1::2]
        return remaining_nums
    if n % 2 != 0:
        remaining_nums = array[0::2]
        return remaining_nums


if __name__ == "__main__":
    main()