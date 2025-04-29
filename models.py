"""
Data models for the Ecotrack project.

This module defines the data structures used throughout the application:
- FetchOutput: Container for raw data fetched from external sources
- PopulateOutput: Container for database table references
- AggregateOutput: Container for aggregated analysis results

Each output type has specific subclasses for commerce, industry, and service data.
"""

import pandas as pd
from dataclasses import dataclass

# Fetch output classes
@dataclass
class CommerceFetching:
    """Container for commerce-related fetched data."""
    group: pd.DataFrame
    volume: pd.DataFrame
    revenue: pd.DataFrame
    expense: pd.DataFrame

@dataclass
class IndustryFetching:
    """Container for industry-related fetched data."""
    activity: pd.DataFrame
    activity_CNAE: pd.DataFrame
    production: pd.DataFrame
    revenue: pd.DataFrame

@dataclass
class ServiceFetching:
    """Container for service-related fetched data."""
    segment: pd.DataFrame
    volume: pd.DataFrame
    revenue: pd.DataFrame

@dataclass
class FetchOutput:
    """Container for all fetched data from Sidra IBGE sources."""
    commerce: CommerceFetching
    industry: IndustryFetching
    service: ServiceFetching

# Populate output classes
@dataclass
class CommercePopulate:
    """Container for commerce-related table references."""
    group_table: str
    volume_table: str
    revenue_table: str
    expense_table: str

@dataclass
class IndustryPopulate:
    """Container for industry-related table references."""
    activity_table: str
    activity_CNAE_table: str
    production_table: str
    revenue_table: str

@dataclass
class ServicePopulate:
    """Container for service-related table references."""
    segment_table: str
    volume_table: str
    revenue_table: str

@dataclass
class PopulateOutput:
    """Container for database table references after data population."""
    commerce: CommercePopulate
    industry: IndustryPopulate
    service: ServicePopulate

# Aggregate output classes
@dataclass
class CommerceAggregate:
    """Container for commerce-related analysis results."""
    volume: str
    division: str
    ranking: str
    revenue_expense: str
    revenue_expense_grouped: str

@dataclass
class IndustryAggregate:
    """Container for industry-related analysis results."""
    production: str
    revenue: str = None
    revenue_yearly: str = None

@dataclass
class ServiceAggregate:
    """Container for service-related analysis results."""
    volume: str
    volume_ranking: str
    revenue: str
    revenue_ranking: str

@dataclass
class AggregateOutput:
    """Container for aggregated analysis results."""
    commerce: CommerceAggregate
    industry: IndustryAggregate
    service: ServiceAggregate