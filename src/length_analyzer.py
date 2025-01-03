from typing import Dict, List
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class LengthAnalyzer:
    def __init__(self, expected_length: int, tolerance: int):
        self.expected_length = expected_length
        self.tolerance = tolerance
        
    def categorize_sequence(self, sequence: str) -> str:
        length = len(sequence)
        min_length = self.expected_length - self.tolerance
        max_length = self.expected_length + self.tolerance
        
        if length < min_length:
            return 'short'
        elif length > max_length:
            return 'long'
        return 'valid'
        
    def analyze_distribution(self, sequences: List[str]) -> Dict[str, int]:
        distribution = defaultdict(int)
        for seq in sequences:
            category = self.categorize_sequence(seq)
            distribution[category] += 1
        return dict(distribution)