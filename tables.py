#tables.py
import logging
from db import get_db_connection

def create_table(query, table_name):
    """Create a generic table from a query."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
        logging.info(f"{table_name} created or already exists.")
    except Exception as e:
        logging.error(f"Error creating {table_name} table: {str(e)}")
        raise

def create_commerce_tables():
    
    """Create all tables related to commerce."""
    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_group (
            id SERIAL PRIMARY KEY,
            group_name TEXT NOT NULL UNIQUE
        );
    """, "commerce_group")

    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_company_count (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            count NUMERIC,
            UNIQUE (id_commerce_group, date)
        );
    """, "commerce_company_count")

    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_revenue (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            revenue NUMERIC,
            UNIQUE (id_commerce_group, date)
        );
    """, "commerce_revenue")

    create_table("""
        CREATE TABLE IF NOT EXISTS commerce_expense (
            id SERIAL PRIMARY KEY,
            id_commerce_group INTEGER REFERENCES commerce_group(id),
            date TEXT,
            expense NUMERIC,
            UNIQUE (id_commerce_group, date)
        );
    """, "commerce_expense")

def create_industry_tables():
  
    """Create all tables related to industry."""
    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_activity (
            id SERIAL PRIMARY KEY,
            activity TEXT NOT NULL UNIQUE
        );
    """, "industrial_activity")

    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_activity_CNAE (
            id SERIAL PRIMARY KEY,
            activity TEXT NOT NULL UNIQUE
        );
    """, "industrial_activity_CNAE")

    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_production (
            id SERIAL PRIMARY KEY,
            id_activity INTEGER REFERENCES industrial_activity(id),
            date TEXT,
            production NUMERIC,
            UNIQUE (id_activity, date)   
        );
    """, "industrial_production")

    create_table("""
        CREATE TABLE IF NOT EXISTS industrial_revenue (
            id SERIAL PRIMARY KEY,
            id_activity_CNAE INTEGER REFERENCES industrial_activity_CNAE(id),
            date TEXT,
            revenue NUMERIC,
            UNIQUE (id_activity_CNAE, date)
        );
    """, "industrial_revenue")

def create_service_tables():

    """Create all tables related to services."""
    create_table("""
        CREATE TABLE IF NOT EXISTS service_segment (
            id SERIAL PRIMARY KEY,
            service TEXT NOT NULL UNIQUE
        );
    """, "service_segment")

    create_table("""
        CREATE TABLE IF NOT EXISTS service_volume (
            id SERIAL PRIMARY KEY,
            id_service INTEGER REFERENCES service_segment(id),
            date TEXT,
            volume NUMERIC,
            UNIQUE (id_service, date)
        );
    """, "service_volume")

    create_table("""
        CREATE TABLE IF NOT EXISTS service_revenue (
            id SERIAL PRIMARY KEY,
            id_service INTEGER REFERENCES service_segment(id),
            date TEXT,
            revenue NUMERIC,
            UNIQUE (id_service, date)            
        );
    """, "service_revenue")


    