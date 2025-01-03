import pytest
from src.primer_analyzer import PrimerAnalyzer

def test_primer_dimer_detection():
    analyzer = PrimerAnalyzer("tests/data/test_primers.fasta", 100)
    
    # Test sequence with primer dimer
    dimer_seq = "ACGTACGTACGTTGCATGCATGCA"
    assert analyzer.detect_primer_dimers(dimer_seq) == True
    
    # Test sequence without primer dimer
    normal_seq = "ATCGATCGATCGATCGATCG"
    assert analyzer.detect_primer_dimers(normal_seq) == False
