"""
Data fetching module for the Ecotrack project.

This module handles:
- Fetching data from SIDRA API for commerce, industry, and services
- Data cleaning and transformation
- Error handling and logging for API requests
- Security measures for data validation

The module uses sidrapy for API interactions and pandas for data manipulation.
"""

import models
import pandas as pd
import sidrapy

import logging
from requests import RequestException

# Classification codes for different data categories
classification_commerce = ("11070/4765,4766,4767,4768,4778,6554,6654,6799,6800,"
                            "90130,90131,90132,90152,90156,90157,106765,106774")
classification_industry = ("544/129314,129315,129316")
classification_industry_CNAE = ("12762/116881,116884,116887,116897,116905,116911,"
                                "116952,116960,116965,116985,116994,117007,117015,"
                                "117029,117039,117048,117082,117089,117099,117116,"
                                "117136,117159,117179,117196,117229,117245,117261,"
                                "117267,117283")
classifications_service_volume = {"11046": "56726", "1274": "all"}
classifications_service_revenue = {"11046": "56725", "1274": "all"}

def fetch() -> models.FetchOutput:
    """
    Main function to fetch all required data categories.
    
    Returns:
        models.FetchOutput: Structured data containing commerce, industry, and service information
    """
    # Fetch commerce data
    commerce_group = fetch_commerce_group()
    commerce_volume = fetch_commerce_volume()
    commerce_revenue = fetch_commerce_revenue()
    commerce_expense = fetch_commerce_expense()
    
    # Fetch industry data
    industry_activity = fetch_industry_activity()
    industry_activity_CNAE = fetch_industry_activity_CNAE()
    industry_production = fetch_industry_production()
    industry_revenue = fetch_industry_revenue()
    
    # Fetch service data
    service_segment = fetch_service_segment()
    service_volume = fetch_service_volume()
    service_revenue = fetch_service_revenue()

    # Structure the data into appropriate models
    commerce = models.CommerceFetching(
        group=commerce_group,
        volume=commerce_volume,
        revenue=commerce_revenue,
        expense=commerce_expense
    )
    industry = models.IndustryFetching(
        activity=industry_activity,
        activity_CNAE=industry_activity_CNAE,
        production=industry_production,
        revenue=industry_revenue
    )
    service = models.ServiceFetching(
        segment=service_segment,
        volume=service_volume,
        revenue=service_revenue
    )
    return models.FetchOutput(
        commerce=commerce,
        industry=industry,
        service=service
    )

# Commerce data fetching functions
def fetch_commerce_group() -> pd.DataFrame:
    """Fetch commerce group data."""
    data = fetch_data(
        table_code="1403",
        territorial_level="1",
        variable="310",
        classification=classification_commerce,
        classifications=None,
        period="last 2"
    )
    return data

def fetch_commerce_volume() -> pd.DataFrame:
    """Fetch commerce volume data for the last 12 years."""
    data = fetch_data(
        table_code="1403",
        territorial_level="1",
        variable="310",
        classification=classification_commerce,
        classifications=None,
        period="last 12"
    )
    return data

def fetch_commerce_revenue() -> pd.DataFrame:
    """Fetch commerce revenue data for the last 12 years."""
    data = fetch_data(
        table_code="1400",
        territorial_level="1",
        variable="501",
        classification=classification_commerce,
        classifications=None,
        period="last 12"
    )
    return data

def fetch_commerce_expense() -> pd.DataFrame:
    """Fetch commerce expense data for the last 12 years."""
    data = fetch_data(
        table_code="1401",
        territorial_level="1",
        variable="1401",
        classification=classification_commerce,
        classifications=None,
        period="last 12"
    )
    return data

# Industry data fetching functions
def fetch_industry_activity() -> pd.DataFrame:
    """Fetch industry activity data."""
    data = fetch_data(
        table_code="8888",
        territorial_level="1",
        variable="12607",
        classification=classification_industry,
        classifications=None,
        period="last 2"
    )
    return data

def fetch_industry_activity_CNAE() -> pd.DataFrame:
    """Fetch industry activity CNAE data."""
    data = fetch_data(
        table_code="1853",
        territorial_level="1",
        variable="805",
        classification=classification_industry_CNAE,
        classifications=None,
        period="last 2"
    )
    return data

def fetch_industry_production() -> pd.DataFrame:
    """Fetch industry production data for the last 60 months."""
    data = fetch_data(
        table_code="8888",
        territorial_level="1",
        variable="12607",
        classification=classification_industry,
        classifications=None,
        period="last 60"
    )
    return data

def fetch_industry_revenue() -> pd.DataFrame:
    """Fetch industry revenue data for the last 12 years."""
    data = fetch_data(
        table_code="1853",
        territorial_level="1",
        variable="805",
        classification=classification_industry_CNAE,
        classifications=None,
        period="last 12"
    )
    return data

# Service data fetching functions
def fetch_service_segment() -> pd.DataFrame:
    """Fetch service segment data."""
    data = fetch_data(
        table_code="8163",
        territorial_level="1",
        variable="7168",
        classification=None,
        classifications=classifications_service_volume,
        period="last 2"
    )
    return data

def fetch_service_volume() -> pd.DataFrame:
    """Fetch service volume data for the last 60 months."""
    data = fetch_data(
        table_code ="8163",
        territorial_level="1",
        variable="7168",
        classification=None,
        classifications=classifications_service_volume,
        period="last 60"
    )
    return data

def fetch_service_revenue() -> pd.DataFrame:
    """Fetch service revenue data for the last 60 months."""
    data = fetch_data(
        table_code="8163",
        territorial_level="1",
        variable="7168",
        classification=None,
        classifications=classifications_service_revenue,
        period="last 60"
    )
    return data

def fetch_data(table_code, territorial_level, variable, classification, classifications, period):
    """
    Generic function to fetch and process data from SIDRA API.
    
    Args:
        table_code (str): SIDRA table identifier
        territorial_level (str): Geographic level of the data
        variable (str): Variable code to fetch
        classification (str): Classification code for the data
        classifications (dict): Additional classifications if needed
        period (str): Time period to fetch (e.g., "last 12")
        
    Returns:
        pd.DataFrame: Processed data frame with standardized columns
        
    Raises:
        RequestException: If there's an error connecting to the API
        Exception: For other unexpected errors during data processing
    """
    try:
        # Fetch data from SIDRA API
        df = sidrapy.get_table(
            table_code=table_code,
            territorial_level=territorial_level,
            ibge_territorial_code="all", 
            variable=variable,
            classification=classification,
            classifications=classifications,
            period=period,
        )

        # Define values to be excluded from the dataset
        unwanted_values = {'Total', 'Índice de receita nominal de serviços'}

        # Determine which column to use based on classification type
        if classifications is not None:
            df_column = "D5N"
        else:
            df_column = "D4N"

        # Validate required column exists
        if df_column not in df.columns:
            logging.error(f"Column {df_column} not found in table {table_code}")
            raise ValueError(f"Column {df_column} not found in table {table_code}")

        # Process and clean the data
        df = df.iloc[1:]  # Remove header row
        df["date"] = df["D2N"].astype(str)
        df = df.dropna(subset=["date", df_column, "V"])
           
        # Replace invalid non numeric values with 0
        df["V"] = df["V"].replace(["-", "..."], 0)

        # Remove unwanted values
        df = df[~df[df_column].isin(unwanted_values)]

        # Check if we have valid data after cleaning
        if df.empty:
            logging.warning(f"No valid data found after cleaning for table {table_code}")
            return pd.DataFrame()
            
        # Select and rename columns
        df = df[["V", "D2N", df_column, "date"]]
        df.columns = ["value", "raw_date", "type", "date"]

        logging.info(f"{len(df)} records extracted from table {table_code}")
        return df
        
    except RequestException as e:
        logging.error(f"Connection error while fetching data from table {table_code}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while fetching data from table {table_code}: {str(e)}")
        raise
