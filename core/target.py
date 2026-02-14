import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class Target:
    domain: str
    mode: str
    start_time: float = field(default_factory=time.time)
    
    # Assets
    subdomains: List[str] = field(default_factory=list)
    live_hosts: List[Dict] = field(default_factory=list)
    cloud_assets: List[Dict] = field(default_factory=list)
    
    # Findings
    technologies: Dict = field(default_factory=dict)
    vulnerabilities: List[Dict] = field(default_factory=list)
    email_security: Dict = field(default_factory=dict)
    endpoints: List[str] = field(default_factory=list) # NEW
    
    # State
    completed_phases: List[str] = field(default_factory=list)
    
    def save(self):
        data_dir = Path("data/sessions")
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{self.domain}.json"
        with open(file_path, "w") as f:
            json.dump(asdict(self), f, indent=4)
    
    @classmethod
    def load(cls, domain):
        file_path = Path(f"data/sessions/{domain}.json")
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
            # Safe Load: Only load keys that exist in our class
            valid_keys = cls.__annotations__.keys()
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered_data)
        return None
