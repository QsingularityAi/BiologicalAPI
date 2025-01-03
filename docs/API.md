# API Documentation

## FastqProcessor

### Methods
- `validate_files()`: Validates input FASTQ files
- `process_reads()`: Generator yielding processed read pairs

## PrimerAnalyzer

### Methods
- `detect_primer_dimers(sequence)`: Detects primer dimers in sequence
- `find_primer_matches(sequence)`: Finds primer matches with errors allowed

## LengthAnalyzer

### Methods
- `categorize_sequence(sequence)`: Categorizes sequence by length
- `analyze_distribution(sequences)`: Analyzes length distribution