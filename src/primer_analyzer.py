from typing import List, Dict, Tuple
from Bio import SeqIO
from Bio.Seq import Seq
import logging

logger = logging.getLogger(__name__)

class PrimerAnalyzer:
    def __init__(self, primer_file: str, max_dimer_length: int):
        self.primers = self._load_primers(primer_file)
        self.max_dimer_length = max_dimer_length
        
    def _load_primers(self, primer_file: str) -> Dict[str, str]:
        primers = {}
        try:
            for record in SeqIO.parse(primer_file, "fasta"):
                primers[record.id] = str(record.seq)
            return primers
        except Exception as e:
            logger.error(f"Failed to load primers: {str(e)}")
            raise
            
    def detect_primer_dimers(self, sequence: str) -> bool:
        if len(sequence) > self.max_dimer_length:
            return False
            
        for primer_name, primer_seq in self.primers.items():
            rc_primer = str(Seq(primer_seq).reverse_complement())
            if self._find_primer_match(sequence, primer_seq) and \
               self._find_primer_match(sequence, rc_primer):
                return True
        return False
        
    def _find_primer_match(self, sequence: str, primer: str, max_errors: int = 2) -> bool:
        # Simple implementation allowing for mismatches
        for i in range(len(sequence) - len(primer) + 1):
            errors = sum(1 for x, y in zip(sequence[i:i+len(primer)], primer) if x != y)
            if errors <= max_errors:
                return True
        return False