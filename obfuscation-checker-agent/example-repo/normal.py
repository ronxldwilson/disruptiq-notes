#!/usr/bin/env python3
"""
Normal, well-documented Python code
This file demonstrates clean, readable code structure
"""

def calculate_sum(numbers):
    """
    Calculate the sum of a list of numbers.

    Args:
        numbers (list): List of numeric values

    Returns:
        float: Sum of all numbers
    """
    total = 0.0
    for number in numbers:
        total += number
    return total

def main():
    """Main function to demonstrate the calculator."""
    test_numbers = [1, 2, 3, 4, 5]
    result = calculate_sum(test_numbers)
    print(f"The sum of {test_numbers} is {result}")

if __name__ == "__main__":
    main()
