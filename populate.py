"""
Database population module for the Ecotrack project.

This module handles:
- Converting fetched data into database records
- Creating necessary database tables if they don't exist
- Populating tables with data from external sources
- Error handling and logging for the population process

The module uses a structured approach to populate different sectors:
- Commerce data (groups, volumes, revenues, expenses)
- Industry data (activities, production, revenue)
- Service data (segments, volumes, revenues)
"""

import logging
import models

from db.db import get_db_connection
from psycopg.errors import OperationalError, DatabaseError

logger = logging.getLogger(__name__)

def populate(data: models.FetchOutput) -> models.PopulateOutput:
    """
    Executes the complete data population pipeline.
    
    Args:
        data: Container with fetched data from external sources
        
    Returns:
        PopulateOutput: References to all populated tables
    """
    commerce_data = populate_commerce(data.commerce)
    industry_data = populate_industry(data.industry)
    service_data = populate_service(data.service)
    return models.PopulateOutput(commerce_data, industry_data, service_data)

def populate_commerce(data: models.CommerceFetching) -> models.CommercePopulate:
    """
    Populates all commerce-related tables.
    
    Args:
        data: Container with commerce fetched data
        
    Returns:
        CommercePopulate: References to populated commerce tables
    """
    group_table = populate_commerce_group(data)
    volume_table = populate_commerce_volume(data)
    revenue_table = populate_commerce_revenue(data)
    expense_table = populate_commerce_expense(data)
    
    return models.CommercePopulate(group_table, volume_table, revenue_table, expense_table)

def populate_industry(data: models.IndustryFetching) -> models.IndustryPopulate:
    """
    Populates all industry-related tables.
    
    Args:
        data: Container with industry fetched data
        
    Returns:
        IndustryPopulate: References to populated industry tables
    """
    activity_table = populate_industry_activity(data)
    activity_CNAE_table = populate_industry_activity_CNAE(data)
    production_table = populate_industry_production(data)
    revenue_table = populate_industry_revenue(data)
    
    return models.IndustryPopulate(activity_table, activity_CNAE_table, production_table, revenue_table)

def populate_service(data: models.ServiceFetching) -> models.ServicePopulate:
    """
    Populates all service-related tables.

    Args:
        data: Container with service fetched data
        
    Returns:
        ServicePopulate: References to populated service tables
    """
    segment_table = populate_service_segment(data)
    volume_table = populate_service_volume(data)
    revenue_table = populate_service_revenue(data)
    
    return models.ServicePopulate(segment_table, volume_table, revenue_table)

# Commerce
def populate_commerce_group(data: models.CommerceFetching) -> str:
    """
    Populates the commerce group table.
    
    Args:
        data: Container with commerce fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "commerce_group"
    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_group (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        );
    """, table_name)  

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.group.iterrows():
                    type_value = row["type"]
                    if not type_value:
                        logger.warning("Skipping empty commerce group type")
                        continue
                        
                    try:
                        cur.execute("""
                            INSERT INTO commerce_group (type) 
                            VALUES (%s) 
                            ON CONFLICT (type) DO NOTHING;
                        """, (type_value,))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting commerce group: {e}")
                        raise
                        
                conn.commit()
                logger.info("Commerce group table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating commerce_group table: {str(e)}")
        raise
    
    return table_name

def populate_commerce_volume(data: models.CommerceFetching) -> str:
    """
    Populates the commerce volume table.
    
    Args:
        data: Container with commerce fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "commerce_volume"
    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_volume (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            volume NUMERIC,
            UNIQUE (id_commerce_group, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.volume.iterrows():
                    type_value = row["type"]

                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete commerce volume data")
                        continue

                    cur.execute(f"SELECT id FROM commerce_group WHERE type = %s;", (type_value,)) 
                    result = cur.fetchone()

                    if not result:
                        logger.warning(f"Type '{type_value}' not found in commerce_group table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO commerce_volume (id_commerce_group, date, volume) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_commerce_group, date) DO NOTHING;
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting commerce volume: {e}")
                        raise
                        
                conn.commit()
                logger.info("Commerce volume table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating commerce_volume table: {str(e)}")
        raise
    
    return table_name

def populate_commerce_revenue(data: models.CommerceFetching) -> str:
    """
    Populates the commerce revenue table.
    
    Args:
        data: Container with commerce fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "commerce_revenue"
    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_revenue (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            revenue NUMERIC,    
            UNIQUE (id_commerce_group, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.revenue.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete commerce revenue data")
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM commerce_group WHERE type = %s;", (type_value,)) 
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in commerce_group table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO commerce_revenue (id_commerce_group, date, revenue) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_commerce_group, date) DO NOTHING;
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting commerce revenue: {e}")
                        raise
                        
                conn.commit()
                logger.info("Commerce revenue table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating commerce_revenue table: {str(e)}")
        raise
    
    return table_name

def populate_commerce_expense(data: models.CommerceFetching) -> str:
    """
    Populates the commerce expense table.
    
    Args:
        data: Container with commerce fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "commerce_expense"
    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_expense (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            expense NUMERIC,
            UNIQUE (id_commerce_group, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.expense.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete commerce expense data")
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM commerce_group WHERE type = %s;", (type_value,)) 
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in commerce_group table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO commerce_expense (id_commerce_group, date, expense) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_commerce_group, date) DO NOTHING;
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting commerce expense: {e}")
                        raise
                        
                conn.commit()
                logger.info("Commerce expense table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating commerce_expense table: {str(e)}")
        raise
    
    return table_name

# Industry
def populate_industry_activity(data: models.IndustryFetching) -> str:
    """
    Populates the industrial activity table.
    
    Args:
        data: Container with industry fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "industrial_activity"
    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_activity (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.activity.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value:
                        logger.warning("Skipping empty industry activity type")
                        continue
                        
                    try:
                        cur.execute("""
                            INSERT INTO industrial_activity (type) 
                            VALUES (%s) 
                            ON CONFLICT (type) DO NOTHING;
                        """, (type_value,))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting industrial activity: {e}")
                        raise
                        
                conn.commit()
                logger.info("Industrial Activity table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating industrial_activity table: {str(e)}")
        raise
    
    return table_name

def populate_industry_activity_CNAE(data: models.IndustryFetching) -> str:
    """
    Populates the industrial activity CNAE table.
    
    Args:
        data: Container with industry fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "industrial_activity_CNAE"
    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_activity_CNAE (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.activity_CNAE.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value:
                        logger.warning("Skipping empty industry activity CNAE type")
                        continue
                        
                    try:
                        cur.execute("""
                            INSERT INTO industrial_activity_CNAE (type) 
                            VALUES (%s) 
                            ON CONFLICT (type) DO NOTHING;
                        """, (type_value,))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting industrial activity CNAE: {e}")
                        raise
                        
                conn.commit()
                logger.info("Industrial Activity CNAE table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating industrial_activity_CNAE table: {str(e)}")
        raise
    
    return table_name

def populate_industry_production(data: models.IndustryFetching) -> str:
    """
    Populates the industrial production table.
    
    Args:
        data: Container with industry fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "industrial_production"
    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_production (
            id SERIAL PRIMARY KEY,
            id_activity INTEGER REFERENCES industrial_activity(id),
            date TEXT,
            production NUMERIC,
            UNIQUE (id_activity, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.production.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete industry production data")
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM industrial_activity WHERE type = %s;", (type_value,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in industrial_activity table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO industrial_production (id_activity, date, production) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_activity, date) DO NOTHING;
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting industrial production: {e}")
                        raise
                        
                conn.commit()
                logger.info("Industrial Production table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating industrial_production table: {str(e)}")
        raise
    
    return table_name

def populate_industry_revenue(data: models.IndustryFetching) -> str:
    """
    Populates the industrial revenue table.
    
    Args:
        data: Container with industry fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "industrial_revenue"
    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_revenue (
            id SERIAL PRIMARY KEY,
            id_activity_CNAE INTEGER REFERENCES industrial_activity_CNAE(id),
            date TEXT,
            revenue NUMERIC,
            UNIQUE (id_activity_CNAE, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.revenue.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete industry revenue data")
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM industrial_activity_CNAE WHERE type = %s;", (type_value,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in industrial_activity_CNAE table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO industrial_revenue (id_activity_CNAE, date, revenue) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_activity_CNAE, date) DO NOTHING;
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting industrial revenue: {e}")
                        raise
                        
                conn.commit()
                logger.info("Industrial Revenue table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating industrial_revenue table: {str(e)}")
        raise
    
    return table_name

# Service
def populate_service_segment(data: models.ServiceFetching) -> str:
    """
    Populates the service segment table.
    
    Args:
        data: Container with service fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "service_segment"
    create_table("""
        CREATE TABLE IF NOT EXISTS service_segment (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL UNIQUE
        );
    """, table_name)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.segment.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value:
                        logger.warning("Skipping empty service segment type")
                        continue
                        
                    try:
                        cur.execute("""
                            INSERT INTO service_segment (type) 
                            VALUES (%s) 
                            ON CONFLICT (type) DO NOTHING;
                        """, (type_value,))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting service segment: {e}")
                        raise
                        
                conn.commit()
                logger.info("Service Segment table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating service_segment table: {str(e)}")
        raise
    
    return table_name

def populate_service_volume(data: models.ServiceFetching) -> str:
    """
    Populates the service volume table.
    
    Args:
        data: Container with service fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "service_volume"
    create_table("""
        CREATE TABLE IF NOT EXISTS service_volume (
            id SERIAL PRIMARY KEY,
            id_service INTEGER REFERENCES service_segment(id),
            date TEXT,
            volume NUMERIC,
            UNIQUE (id_service, date)
        );
    """, table_name)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.volume.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete service volume data") 
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM service_segment WHERE type = %s;", (type_value,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in service_segment table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO service_volume (id_service, date, volume) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_service, date) DO NOTHING;  
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting service volume: {e}")
                        raise
                        
                conn.commit()
                logger.info("Service Volume table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating service_volume table: {str(e)}")
        raise
    
    return table_name

def populate_service_revenue(data: models.ServiceFetching) -> str:
    """
    Populates the service revenue table.
    
    Args:
        data: Container with service fetched data
        
    Returns:
        str: Name of the populated table
        
    Raises:
        Exception: If population fails
    """
    table_name = "service_revenue"
    create_table("""
        CREATE TABLE IF NOT EXISTS service_revenue (
            id SERIAL PRIMARY KEY,
            id_service INTEGER REFERENCES service_segment(id),
            date TEXT,
            revenue NUMERIC,
            UNIQUE (id_service, date)
        );
    """, table_name)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for _, row in data.revenue.iterrows():
                    type_value = row["type"]
                    
                    # Validate input data
                    if not type_value or not row["date"] or row["value"] is None:
                        logger.warning("Skipping incomplete service revenue data")
                        continue
                        
                    # Use parameterized query to prevent SQL injection
                    cur.execute("SELECT id FROM service_segment WHERE type = %s;", (type_value,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"Type '{type_value}' not found in service_segment table.")
                        continue
                    id_type = result[0]

                    try:
                        cur.execute("""
                            INSERT INTO service_revenue (id_service, date, revenue) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (id_service, date) DO NOTHING;      
                        """, (id_type, row["date"], row["value"]))
                    except (OperationalError, DatabaseError) as e:
                        logger.error(f"Database error while inserting service revenue: {e}")
                        raise
                        
                conn.commit()
                logger.info("Service Revenue table populated successfully.")
    except Exception as e:
        logger.error(f"Error populating service_revenue table: {str(e)}")
        raise
    
    return table_name

def create_table(query: str, table_name: str):
    """
    Creates a database table if it doesn't exist.
    
    Args:
        query: SQL query to create the table
        table_name: Name of the table to create
        
    Raises:
        Exception: If table creation fails
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
        logger.info(f"{table_name} created or already exists.")
    except Exception as e:
        logger.error(f"Error creating {table_name} table: {str(e)}")
        raise
