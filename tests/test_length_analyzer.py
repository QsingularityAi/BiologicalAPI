import pytest
from src.length_analyzer import LengthAnalyzer

def test_sequence_categorization():
    analyzer = LengthAnalyzer(400, 50)
    
    # Test various sequence lengths
    assert analyzer.categorize_sequence("A" * 300) == "short"
    assert analyzer.categorize_sequence("A" * 400) == "valid"
    assert analyzer.categorize_sequence("A" * 500) == "long"
