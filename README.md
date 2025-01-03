# Amplicon Analyzer

Tool for detecting primer dimers and off-target amplification in amplicon sequencing data.

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Usage

Basic usage:
```bash
analyze_amplicons --r1 sample_R1.fastq.gz \
                 --r2 sample_R2.fastq.gz \
                 --primers primers.fasta \
                 --config config.json \
                 --output results/
```

## Configuration

Example config.json:
```json
{
    "max_dimer_length": 100,
    "length_tolerance": 50,
    "quality_threshold": 30,
    "expected_length": 400
}
```

## Output Files

1. summary_statistics.csv: Contains per-sample statistics
2. detailed_report.json: Comprehensive analysis results
3. *_length_distribution.png: Length distribution plots per sample
