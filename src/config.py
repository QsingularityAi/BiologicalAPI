from dataclasses import dataclass
from typing import Dict, Any
import json
import yaml

@dataclass
class Config:
    max_dimer_length: int = 100
    length_tolerance: int = 50
    quality_threshold: int = 30
    expected_length: int = 400
    
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        if path.endswith('.json'):
            with open(path) as f:
                data = json.load(f)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            with open(path) as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError("Config file must be JSON or YAML")
        return cls(**data)