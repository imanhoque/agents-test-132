#!/usr/bin/env python3
"""
Test script to verify the robustness of the stock analyzer
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from main import validate_stock_symbol, get_stock_info, format_value
import yfinance as yf

def test_validation():
    """Test input validation"""
    print("Testing input validation...")
    
    tests = [
        ("AAPL", True),
        ("aapl", True),  # Should convert to uppercase
        ("  TSLA  ", True),  # Should trim whitespace
        ("GOOGL", True),
        ("", False),  # Empty string
        ("TOOLONG", False),  # Too long
        ("A1", False),  # Contains number
        ("ABC-D", False),  # Contains hyphen
    ]
    
    passed = 0
    failed = 0
    
    for symbol, should_pass in tests:
        is_valid, result = validate_stock_symbol(symbol)
        if is_valid == should_pass:
            print(f"  ✓ '{symbol}' -> {result if is_valid else 'Invalid'}")
            passed += 1
        else:
            print(f"  ✗ '{symbol}' -> Expected {'valid' if should_pass else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
            failed += 1
    
    print(f"\nValidation tests: {passed} passed, {failed} failed\n")
    return failed == 0

def test_data_fetching():
    """Test data fetching with various symbols"""
    print("Testing data fetching...")
    
    # Test with a known valid symbol
    try:
        stock_data = get_stock_info("AAPL")
        if stock_data['current_price'] is not None:
            print("  ✓ Successfully fetched AAPL data")
            print(f"    Price: {format_value(stock_data['current_price'], '$')}")
            return True
        else:
            print("  ✗ AAPL data missing price")
            return False
    except Exception as e:
        print(f"  ✗ Failed to fetch AAPL data: {str(e)}")
        return False

def test_formatting():
    """Test value formatting functions"""
    print("\nTesting value formatting...")
    
    tests = [
        (1234.56, "$", "", 2, "$1,234.56"),
        (1234567, "$", "", 0, "$1,234,567"),
        (None, "$", "", 2, "N/A"),
        (0.0525, "", "%", 2, "0.05%"),
    ]
    
    passed = 0
    failed = 0
    
    for value, prefix, suffix, decimals, expected in tests:
        result = format_value(value, prefix, suffix, decimals)
        if result == expected:
            print(f"  ✓ {value} -> {result}")
            passed += 1
        else:
            print(f"  ✗ {value} -> Expected '{expected}', got '{result}'")
            failed += 1
    
    print(f"\nFormatting tests: {passed} passed, {failed} failed\n")
    return failed == 0

def test_error_handling():
    """Test error handling for invalid symbols"""
    print("Testing error handling...")
    
    try:
        # This should raise an error
        get_stock_info("INVALIDXXX")
        print("  ✗ Should have raised an error for invalid symbol")
        return False
    except ValueError as e:
        print(f"  ✓ Correctly caught error: {str(e)}")
        return True
    except Exception as e:
        print(f"  ✗ Unexpected error type: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("="*70)
    print("Stock Analyzer Robustness Tests")
    print("="*70 + "\n")
    
    results = []
    
    results.append(("Validation", test_validation()))
    results.append(("Formatting", test_formatting()))
    results.append(("Data Fetching", test_data_fetching()))
    results.append(("Error Handling", test_error_handling()))
    
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("="*70)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

