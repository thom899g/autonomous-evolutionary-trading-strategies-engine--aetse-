"""
AETSE Configuration Management
Centralized configuration for the Autonomous Evolutionary Trading Strategies Engine
Provides environment-based configuration with validation and defaults
"""
import os
from dataclasses import dataclass
from typing import Optional
from datetime import timedelta
import logging

@dataclass
class MarketConfig:
    """Market data configuration"""
    exchange: str = "binance"  # Default exchange
    symbols: list = None  # Will be initialized
    timeframe: str = "1h"  # Default timeframe
    max_historical_bars: int = 1000  # Max bars to fetch
    update_interval_seconds: int = 60  # How often to update data
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

@dataclass
class EvolutionConfig:
    """Genetic algorithm configuration"""
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.15
    crossover_rate: float = 0.7
    elitism_count: int = 5  # Number of best strategies to preserve
    tournament_size: int = 7  # Tournament selection size
    max_strategy_complexity: int = 10  # Max indicators per strategy
    
    def validate(self):
        """Validate configuration parameters"""
        assert 0 <= self.mutation_rate <= 1, "Mutation rate must be between 0 and 1"
        assert 0 <= self.crossover_rate <= 1, "Crossover rate must be between 0 and 1"
        assert self.population_size > 0, "Population size must be positive"
        assert self.elitism_count < self.population_size, "Elitism count must be less than population size"

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: Optional[str] = None
    collection_name: str = "aetse_strategies"
    performance_collection: str = "strategy_performance"
    state_collection: str = "evolution_state"
    
    def __post_init__(self):
        # Try to get from environment if not provided
        if not self.project_id:
            self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        
    def is_configured(self) -> bool:
        """Check if Firebase is properly configured"""
        return bool(self.project_id)

@dataclass
class TradingConfig:
    """Trading execution configuration"""
    paper_trading: bool = True  # Start with paper trading
    max_position_size: float = 0.1  # 10% of portfolio per trade
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    max_drawdown_limit: float = 0.15  # 15% max drawdown
    
    def validate(self):
        """Validate trading parameters"""
        assert 0 < self.max_position_size <= 1, "Position size must be between 0 and 1"
        assert 0 < self.stop_loss_pct < 0.5, "Stop loss must be reasonable"
        assert 0 < self.take_profit_pct < 0.5, "Take profit must be reasonable"

class AETSEConfig:
    """Main configuration class aggregating all configs"""
    
    def __init__(self):
        self.market = MarketConfig()
        self.evolution = EvolutionConfig()
        self.firebase = FirebaseConfig()
        self.trading = TradingConfig()
        self.log_level = logging.INFO
        
        # Validate all configurations
        self.validate()
    
    def validate(self):
        """Validate entire configuration"""
        self.evolution.validate()
        self.trading.validate()
        
        if not self.firebase.is_configured():
            logging.warning("Firebase not configured - using local storage only")
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv("AETSE_LOG_LEVEL"):
            config.log_level = getattr(logging, os.getenv("AETSE_LOG_LEVEL").upper())
        
        return config

# Global configuration instance
config = AETSEConfig.from_env()