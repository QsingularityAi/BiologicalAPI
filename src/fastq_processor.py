from typing import Generator, Tuple, List
from Bio import SeqIO
import gzip
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FastqProcessor:
    def __init__(self, r1_path: str, r2_path: str, quality_threshold: int):
        self.r1_path = Path(r1_path)
        self.r2_path = Path(r2_path)
        self.quality_threshold = quality_threshold
        
    def validate_files(self) -> bool:
        if not self.r1_path.exists() or not self.r2_path.exists():
            return False
        try:
            self._open_fastq(self.r1_path).__next__()
            self._open_fastq(self.r2_path).__next__()
            return True
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return False
    
    def _open_fastq(self, path: Path):
        if str(path).endswith('.gz'):
            return SeqIO.parse(gzip.open(path, 'rt'), 'fastq')
        return SeqIO.parse(path, 'fastq')
    
    def process_reads(self) -> Generator[Tuple[str, float], None, None]:
        r1_parser = self._open_fastq(self.r1_path)
        r2_parser = self._open_fastq(self.r2_path)
        
        for r1, r2 in zip(r1_parser, r2_parser):
            if self._check_quality(r1) and self._check_quality(r2):
                merged_seq = self._merge_reads(r1, r2)
                avg_quality = (sum(r1.letter_annotations["phred_quality"]) + 
                             sum(r2.letter_annotations["phred_quality"])) / (len(r1) + len(r2))
                yield merged_seq, avg_quality
                
    def _check_quality(self, record) -> bool:
        return min(record.letter_annotations["phred_quality"]) >= self.quality_threshold
        
    def _merge_reads(self, r1, r2) -> str:
        return str(r1.seq + r2.seq)
    