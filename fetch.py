""" This module is responsible for fetching data from the SIDRA API (IBGE data service)
    It provides functions to fetch different types of economic data (commerce, industry, services)
"""
import logging 
import sidrapy

from requests.exceptions import RequestException  
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

""" Definition of classification codes for different economic sectors.
    These codes are defined by SIDRA
"""
# Classification codes for the commerce sector
classification_commerce = ("11070/4765,4766,4767,4768,4778,6554,6654,6799,6800,"
                            "90130,90131,90132,90152,90156,90157,106765,106774")

# Industry tables have different classification codes

# Classification codes for the industry sector
classification_industry = ("544/129314,129315,129316")

# Industry sector CNAE codes
classification_industry_CNAE = ("12762/116881,116884,116887,116897,116905,116911,"
                                "116952,116960,116965,116985,116994,117007,117015,"
                                "117029,117039,117048,117082,117089,117099,117116,"
                                "117136,117159,117179,117196,117229,117245,117261,"
                                "117267,117283")

# Classification codes for the services sector
classifications_service_volume = {"11046": "56726", "1274": "all"}
classifications_service_revenue = {"11046": "56725", "1274": "all"}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))

def fetch_data(table_code, territorial_level, variable, classification, classifications, period):
    """Fetches data from SIDRA API and returns a clean DataFrame
    
    Args:
        table_code (str)
        territorial_level (str)
        variable (str)
        classification (str)
        classifications (dict)
        period (str)
        
    Returns:
        list: List of dictionaries containing the fetched data
        
    Raises:
        RequestException: If there's an error connecting to the SIDRA API
    """
    try:
        logger.info(f"Starting data fetch from table {table_code}")
        
        df = sidrapy.get_table(
            table_code=table_code,
            territorial_level=territorial_level,
            ibge_territorial_code="all", 
            variable=variable,
            classification=classification,
            classifications=classifications,
            period=period,
        )
        
        if df.empty:
            logger.warning(f"No data found for table {table_code}")
            return []

        if classifications is not None:
            df_column = "D5N"
        else:
            df_column = "D4N"

        if df_column not in df.columns:
            logger.error(f"Column {df_column} not found in table {table_code}")
            return []

        df = df.iloc[1:]
        df["date"] = df["D2N"].astype(str)
        df = df.dropna(subset=["date", df_column, "V"])

        if df.empty:
            logger.warning(f"No valid data found after cleaning for table {table_code}")
            return []

        logger.info(f"{len(df)} records extracted from table {table_code}")
        return df.to_dict(orient="records")
        
    except RequestException as e:
        logger.error(f"Connection error while fetching data from table {table_code}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching data from table {table_code}: {str(e)}")
        return []

def fetch_commerce_group_descriptions():
    """Returns a list of commerce groups.
    
    This function fetches the list of all commerce groups available
    in the SIDRA API. It is used to populate dropdown menus and filters.
    
    Returns:
        list: List of commerce group names
    """
    try:
        records = fetch_data("1403", "1", "310", classification_commerce, None, "last 2")
        return list(set(record["D4N"] for record in records if record.get("D4N")))
    except Exception as e:
        logger.error(f"Error fetching commerce group descriptions: {str(e)}")
        return []

def fetch_industrial_activity_descriptions():
    """Returns a list of industrial activities.
    
    This function fetches the list of all industrial activities available
    in the SIDRA API. It is used to populate dropdown menus and filters.
    
    Returns:
        list: List of industrial activity names
    """
    try:
        records = fetch_data("8888", "3", "12607", classification_industry, None, "last 60")
        return list(set(record["D4N"] for record in records if record.get("D4N")))
    except Exception as e:
        logger.error(f"Error fetching industrial activity descriptions: {str(e)}")
        return []

def fetch_industrial_activity_descriptions_CNAE():
    """Returns a list of industrial activities divided into extractive and manufacturing.
    
    This function fetches industrial activities using the CNAE classification system.
    
    Returns:
        list: List of industrial activity names according to CNAE classification
    """
    try:
        records = fetch_data("1853", "1", "805", classification_industry_CNAE, None, "last 2")
        return list(set(record["D4N"] for record in records if record.get("D4N")))
    except Exception as e:
        logger.error(f"Error fetching industrial activity CNAE descriptions: {str(e)}")
        return []

def fetch_service_segment_descriptions():
    """Returns a list of service segments.
    
    This function fetches the list of all service segments available
    in the SIDRA API. It excludes total values and nominal revenue indices
    to provide only meaningful segment categories.
    
    Returns:
        list: List of service segment names
    """
    try:
        records = fetch_data("8163", "1", "7168", None, classifications_service_volume, "last 2")
        unwanted_values = {'Total', 'Nominal service revenue index'}
        return list(set(record["D5N"] for record in records if record.get("D5N") and record["D5N"] not in unwanted_values))
    except Exception as e:
        logger.error(f"Error fetching service segment descriptions: {str(e)}")
        return []

