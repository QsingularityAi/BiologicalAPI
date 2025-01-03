# src/cli.py
import click
import logging
from pathlib import Path
from typing import Dict, List
import sys

from .config import Config
from .fastq_processor import FastqProcessor
from .primer_analyzer import PrimerAnalyzer
from .length_analyzer import LengthAnalyzer
from .visualizer import Visualizer
from .report_generator import ReportGenerator
from .batch_processor import BatchProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmpliconAnalyzer:
    def __init__(self, config: Config, output_dir: str):
        self.config = config
        self.output_dir = output_dir
        self.visualizer = Visualizer(output_dir)
        self.report_generator = ReportGenerator(output_dir)
        
    def analyze_sample(self, r1_path: str, r2_path: str, primer_file: str) -> dict:
        fastq_proc = FastqProcessor(r1_path, r2_path, self.config.quality_threshold)
        primer_anal = PrimerAnalyzer(primer_file, self.config.max_dimer_length)
        length_anal = LengthAnalyzer(self.config.expected_length, self.config.length_tolerance)
        
        if not fastq_proc.validate_files():
            raise ValueError("Invalid FASTQ files")
            
        sequences = []
        lengths = []
        primer_dimers = 0
        
        for seq, quality in fastq_proc.process_reads():
            sequences.append(seq)
            lengths.append(len(seq))
            if primer_anal.detect_primer_dimers(seq):
                primer_dimers += 1
                
        length_dist = length_anal.analyze_distribution(sequences)
        
        sample_id = Path(r1_path).stem.split('_')[0]
        total_reads = len(sequences)
        
        self.visualizer.plot_length_distribution(
            lengths, sample_id, self.config.max_dimer_length,
            self.config.expected_length, self.config.length_tolerance
        )
        
        return {
            'sample_id': sample_id,
            'total_reads': total_reads,
            'primer_dimer_count': primer_dimers,
            'primer_dimer_percentage': (primer_dimers / total_reads) * 100,
            'short_offtarget_count': length_dist.get('short', 0),
            'long_offtarget_count': length_dist.get('long', 0),
            'valid_amplicon_count': length_dist.get('valid', 0)
        }

@click.command()
@click.option('--input-dir', required=True, help='Directory containing FASTQ files')
@click.option('--primers', required=True, help='Primer FASTA file')
@click.option('--config', required=True, help='Configuration file')
@click.option('--output', required=True, help='Output directory')
@click.option('--max-workers', type=int, help='Maximum number of parallel processes')
@click.option('--batch-size', type=int, default=1000000, help='Number of reads to process in each batch')
def main(input_dir: str, primers: str, config: str, output: str, max_workers: int, batch_size: int):
    """Process multiple samples with parallel processing and memory optimization."""
    try:
        # Load configuration
        config_data = Config.from_file(config)
        config_dict = {
            **vars(config_data),
            'primer_file': primers
        }
        
        # Initialize batch processor
        processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output,
            max_workers=max_workers,
            batch_size=batch_size
        )
        
        # Find and validate sample pairs
        logger.info("Scanning for sample pairs...")
        sample_pairs = processor.find_sample_pairs()
        logger.info(f"Found {len(sample_pairs)} valid sample pairs")
        
        # Process samples
        results = processor.process_samples(sample_pairs, config_dict)
        
        if results:
            # Generate reports
            logger.info("Generating reports...")
            visualizer = Visualizer(output)
            report_gen = ReportGenerator(output)
            
            # Create visualizations
            visualizer.create_visualizations(results)
            
            # Generate reports
            report_gen.generate_summary_csv(results)
            report_gen.generate_detailed_report(results, config_dict)
            report_gen.generate_html_report(results, config_dict)
            
            logger.info(f"Successfully processed {len(results)} samples")
        else:
            logger.error("No results generated")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        sys.exit(1)
        
if __name__ == '__main__':
    main()