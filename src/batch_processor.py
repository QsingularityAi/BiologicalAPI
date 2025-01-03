from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Tuple, Generator
import logging
from pathlib import Path
import os
import re
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm
from Bio import SeqIO
import gzip


logger = logging.getLogger(__name__)

@dataclass
class SamplePair:
    sample_id: str
    r1_path: Path
    r2_path: Path
    
    @property
    def valid(self) -> bool:
        return self.r1_path.exists() and self.r2_path.exists()

class BatchProcessor:
    def __init__(self, 
                 input_dir: str, 
                 output_dir: str, 
                 max_workers: int = None,
                 batch_size: int = 1000000):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers or os.cpu_count()
        self.batch_size = batch_size
        
    def find_sample_pairs(self) -> List[SamplePair]:
        """Find and validate all sample pairs in the input directory."""
        sample_pairs = []
        r1_pattern = re.compile(r'(.+)_R1')
        
        # Find all R1 files
        for r1_file in self.input_dir.glob("*_R1*.fastq.gz"):
            sample_match = r1_pattern.match(r1_file.stem)
            if not sample_match:
                continue
                
            sample_id = sample_match.group(1)
            r2_file = r1_file.parent / f"{sample_id}_R2.fastq.gz"
            
            pair = SamplePair(
                sample_id=sample_id,
                r1_path=r1_file,
                r2_path=r2_file
            )
            
            if pair.valid:
                sample_pairs.append(pair)
            else:
                logger.warning(f"Incomplete pair found for sample {sample_id}")
        
        return sample_pairs

    def _read_fastq(self, file_path: Path) -> Generator:
        """Read FASTQ file and yield sequences."""
        if str(file_path).endswith('.gz'):
            handle = gzip.open(str(file_path), 'rt')
        else:
            handle = open(str(file_path), 'rt')
            
        try:
            for record in SeqIO.parse(handle, 'fastq'):
                yield str(record.seq)
        finally:
            handle.close()

    def process_samples(self, sample_pairs: List[SamplePair], config: Dict) -> List[Dict]:
        """Process multiple samples in parallel with progress tracking."""
        if len(sample_pairs) < 3:
            raise ValueError(f"Found only {len(sample_pairs)} valid sample pairs. Minimum 3 required.")

        results = []
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single_sample, pair, config): pair
                for pair in sample_pairs
            }
            
            for future in tqdm(as_completed(futures), total=len(sample_pairs), desc="Processing samples"):
                sample = futures[future]
                try:
                    result = future.result()
                    if result:  # Only append if we got valid results
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error processing sample {sample.sample_id}: {str(e)}")
        
        if not results:
            raise ValueError("No samples were successfully processed")
        return results

    def _process_single_sample(self, sample: SamplePair, config: Dict) -> Dict:
        """Process a single sample."""
        total_reads = 0
        sequences = []
        
        # Read R1 file
        for seq in self._read_fastq(sample.r1_path):
            sequences.append(seq)
            total_reads += 1
            
        # Process sequences in batches
        primer_dimers = 0
        short_count = 0
        long_count = 0
        valid_count = 0
        
        for seq in sequences:
            length = len(seq)
            
            # Count primer dimers
            if length <= config['max_dimer_length']:
                primer_dimers += 1
                
            # Categorize by length
            if length < (config['expected_length'] - config['length_tolerance']):
                short_count += 1
            elif length > (config['expected_length'] + config['length_tolerance']):
                long_count += 1
            else:
                valid_count += 1
        
        return {
            'sample_id': sample.sample_id,
            'total_reads': total_reads,
            'primer_dimer_count': primer_dimers,
            'primer_dimer_percentage': (primer_dimers / total_reads * 100) if total_reads > 0 else 0,
            'short_offtarget_count': short_count,
            'long_offtarget_count': long_count,
            'valid_amplicon_count': valid_count
        }