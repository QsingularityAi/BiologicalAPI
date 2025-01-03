import pytest
from pathlib import Path
from src.fastq_processor import FastqProcessor

def test_fastq_processor_validation():
    processor = FastqProcessor(
        "tests/data/test_r1.fastq",
        "tests/data/test_r2.fastq",
        30
    )
    assert processor.validate_files() == True

def test_fastq_processor_invalid_files():
    processor = FastqProcessor(
        "nonexistent_r1.fastq",
        "nonexistent_r2.fastq",
        30
    )
    assert processor.validate_files() == False