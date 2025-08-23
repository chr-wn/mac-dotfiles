#!/usr/bin/env python3

# This should show type errors
def add_numbers(a: int, b: int) -> int:
    return a + b

# Type error - passing string to int function
result = add_numbers("hello", 5)

# Undefined variable error
print(undefined_var)

# Import error
import nonexistent_module

# Wrong return type
def get_name() -> str:
    return 42