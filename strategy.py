"""
Trading Strategy Representation
Defines the genetic representation of trading strategies with indicators, rules, and actions
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import random
import hashlib
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Indicator:
    """Technical indicator representation for strategy genes"""
    
    # Available indicators with their parameter ranges
    INDICATORS = {
        "sma": {"params": ["period"], "period_range": (5, 200)},
        "ema": {"params": ["period"], "period_range": (5, 200)},
        "rsi": {"params": ["period"], "period_range": (5, 100)},
        "macd": {"params": ["fast", "slow", "signal"], "fast_range": (5, 50), "slow_range": (10, 100), "signal_range": (5, 20)},
        "bbands": {"params": ["period", "std_dev"], "period_range": (5, 100), "std_range": (1, 3)},
        "atr": {"params": ["period"], "period_range": (5, 50)},
        "stoch": {"params": ["k_period", "d_period"], "k_range": (5, 50), "d_range": (1, 10)},
    }
    
    def __init__(self, name: str, params: Dict[str, float]):
        """Initialize indicator with parameters"""
        self.name = name
        self.params = params
        
        # Validate indicator exists
        if name not in self.INDICATORS:
            raise ValueError(f"Unknown indicator: {name}")
        
        # Validate parameters
        self.validate_params()
    
    def validate_params(self):
        """Validate indicator parameters are within acceptable ranges"""
        config = self.INDICATORS[self.name]
        
        for param, value in self.params.items():
            if param in config:
                if isinstance(config[param], tuple):
                    min_val, max_val = config[param]
                    if not min_val <= value <= max_val:
                        self.params[param] = max(min_val, min(value, max_val))
                        logger.warning(f"Adjusted {param} from {value} to {self.params[param]}")
    
    def __str__(self):
        return f"{self.name}({', '.join(f'{k}={v}' for k, v in self.params.items())})"
    
    def to_dict(self) -> Dict:
        """Convert indicator to dictionary for serialization"""
        return {
            "name": self.name,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Indicator':
        """Create indicator from dictionary"""
        return cls(data["name"], data["params"])
    
    @classmethod
    def random(cls) -> 'Indicator':
        """Generate random indicator"""
        name = random.choice(list(cls.INDICATORS.keys()))
        params = {}
        
        # Generate random parameters for this indicator