# Detailed Usage Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/username/amplicon_analyzer.git
cd amplicon_analyzer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python setup.py install
```

## Running Analysis

### Basic Usage

```bash
analyze_amplicons --r1 sample_R1.fastq.gz \
                 --r2 sample_R2.fastq.gz \
                 --primers primers.fasta \
                 --config config.json \
                 --output results/
```

### Configuration Options

#### Quality Threshold
Minimum Phred quality score (default: 30)
```json
{
    "quality_threshold": 30
}
```

#### Length Parameters
```json
{
    "expected_length": 400,
    "length_tolerance": 50,
    "max_dimer_length": 100
}
```

## Output Files

### Summary Statistics (CSV)
Contains per-sample metrics including:
- Total reads
- Primer dimer counts
- Off-target counts
- Valid amplicon counts

### Detailed Report (JSON)
Includes:
- Overall statistics
- Per-sample breakdown
- Configuration used
- Methods description

### Visualizations
Length distribution plots showing:
- Read length histogram
- Marked regions for dimers
- Expected length range
- Off-target regions