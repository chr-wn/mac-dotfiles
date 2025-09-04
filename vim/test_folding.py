#!/usr/bin/env python3
"""
Test file for nvim-ufo folding functionality.
This file contains various Python constructs that should be foldable.
"""

import os
import sys
from typing import List, Dict, Optional

class TestClass:
    """A test class to demonstrate folding."""
    
    def __init__(self, name: str):
        """Initialize the test class."""
        self.name = name
        self.data = []
    
    def add_data(self, item: str) -> None:
        """Add an item to the data list."""
        if item:
            self.data.append(item)
        else:
            print("Empty item not added")
    
    def process_data(self) -> List[str]:
        """Process the data and return results."""
        results = []
        for item in self.data:
            if len(item) > 3:
                results.append(item.upper())
            else:
                results.append(item.lower())
        return results
    
    def complex_method(self, params: Dict[str, str]) -> Optional[str]:
        """A more complex method with nested structures."""
        if not params:
            return None
        
        try:
            for key, value in params.items():
                if key == "special":
                    if value == "test":
                        return "special_test"
                    elif value == "demo":
                        return "special_demo"
                    else:
                        continue
                else:
                    print(f"Processing {key}: {value}")
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        return "processed"

def standalone_function(x: int, y: int) -> int:
    """A standalone function for testing."""
    if x > y:
        result = x * 2
        if result > 100:
            return result // 2
        else:
            return result
    else:
        result = y * 3
        if result < 50:
            return result + 10
        else:
            return result - 5

def another_function():
    """Another function with nested logic."""
    data = {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35}
        ],
        "settings": {
            "theme": "dark",
            "language": "en",
            "notifications": True
        }
    }
    
    for user in data["users"]:
        if user["age"] > 30:
            print(f"{user['name']} is over 30")
        else:
            print(f"{user['name']} is 30 or under")
    
    return data

if __name__ == "__main__":
    # Main execution block
    test_obj = TestClass("test_instance")
    test_obj.add_data("hello")
    test_obj.add_data("world")
    test_obj.add_data("python")
    
    results = test_obj.process_data()
    print("Results:", results)
    
    params = {"special": "test", "normal": "value"}
    complex_result = test_obj.complex_method(params)
    print("Complex result:", complex_result)
    
    func_result = standalone_function(10, 5)
    print("Function result:", func_result)
    
    data = another_function()
    print("Data keys:", list(data.keys()))