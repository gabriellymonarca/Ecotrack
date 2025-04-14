#populate.py
import logging
import pandas as pd
from db import get_db_connection
from fetch import (
    fetch_data, 
    fetch_commerce_group_descriptions, 
    fetch_industrial_activity_descriptions,
    fetch_industrial_activity_descriptions_CNAE,
    fetch_service_segment_descriptions,
    classification_commerce as class_com,
    classification_industry as class_in,
    classification_industry_CNAE as class_in_CNAE,
    classifications_service_volume as class_s_v,
    classifications_service_revenue as class_s_r
)
from tables import (
    create_commerce_tables, 
    create_industry_tables,
    create_service_tables
)

def populate_segment_type_table(table_name, column_name):
    """Populate type of activites table."""
    create_commerce_tables()
    create_industry_tables()
    create_service_tables()
    
    if table_name == "commerce_group":
        segment_types = fetch_commerce_group_descriptions()
    elif table_name == "industrial_activity":
        segment_types = fetch_industrial_activity_descriptions()
    elif table_name == "industrial_activity_CNAE":
        segment_types = fetch_industrial_activity_descriptions_CNAE()
    elif table_name == "service_segment":
        segment_types = fetch_service_segment_descriptions()
    else:
        logging.error(f"Unknown table: {table_name}")
        return
        
    if not segment_types:
        logging.error(f"No data found after fetching for {table_name}.")
        return
    
    unwanted_values = {'Total', 'Índice de receita nominal de serviços'}

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for segment in segment_types:
                    if segment in unwanted_values:
                        continue

                    cur.execute(f"""
                        INSERT INTO {table_name} ({column_name})
                        VALUES (%s) ON CONFLICT ({column_name}) DO NOTHING;
                    """, (segment,))

                conn.commit()
        logging.info(f"{table_name} table populated successfully.")
    except Exception as e:
        logging.error(f"Error populating {table_name} table: " + str(e))
        raise

# Sector_segment_table: Indicates each group for commerce, activity for industry
# Output_table: Is where de data will be loaded, rather for commerce, industry or service 
def populate_table(
    sector_segment_table, output_table, output_table_code, variable, 
    sector_segment_names_column, output_table_values_column, 
    output_table_segment_id_column, classification, classifications, period
    ):
    unwanted_values = {'Total', 'Índice de receita nominal de serviços'}

    """Populates a generic table with data extracted via API."""
    territorial_level = "1"
    records = fetch_data(output_table_code, territorial_level, variable, classification, classifications, period)
    if classifications != None:
        df_column = "D5N"
    else:
        df_column = "D4N"
    
    if not records:
        logging.error(f"No data found for {output_table} table.")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for record in records:
                    type_name = record.get(df_column)
                    date = str(record.get("D2N"))
                    value = record.get("V")
                    if value == "-" or value == "...":
                        value = 0

                    if type_name is None or date is None or pd.isna(value) or type_name in unwanted_values:
                        continue
                    
                    cur.execute(f"SELECT id FROM {sector_segment_table} WHERE {sector_segment_names_column} = %s;", (type_name,))
                    result = cur.fetchone()
                    if not result:
                        logging.warning(f"Data not found in {sector_segment_table} table.")
                        continue
                    id_type = result[0]

                    # Garantir que a data esteja no formato correto (ex: "dezembro 2020")
                    # Se a data já estiver no formato correto, não fazer nada
                    # Se a data estiver em outro formato, converter para o formato correto
                    # Por exemplo, se a data estiver no formato "2020-12", converter para "dezembro 2020"
                    if "-" in date:
                        # Converter de "2020-12" para "dezembro 2020"
                        year, month = date.split("-")
                        month_names = {
                            "01": "janeiro", "02": "fevereiro", "03": "março", "04": "abril",
                            "05": "maio", "06": "junho", "07": "julho", "08": "agosto",
                            "09": "setembro", "10": "outubro", "11": "novembro", "12": "dezembro"
                        }
                        if month in month_names:
                            date = f"{month_names[month]} {year}"

                    cur.execute(f"""
                        INSERT INTO {output_table} ({output_table_segment_id_column}, date, {output_table_values_column})
                        VALUES (%s, %s, %s) ON CONFLICT ({output_table_segment_id_column}, date) DO NOTHING;
                    """, (id_type, date, value))
                conn.commit()
        logging.info(f"Table {output_table} populated successfully.")
    except Exception as e:
        logging.error(f"Error populating {output_table} table: {str(e)}")
        raise

def populate_all_commerce():
    """Populate all commerce tables."""
    populate_segment_type_table("commerce_group", "group_name")
    populate_table("commerce_group", "commerce_company_count", "1403", "310", "group_name", "count", "id_commerce_group", class_com, None, "last 12")
    populate_table("commerce_group", "commerce_revenue", "1400", "501", "group_name", "revenue", "id_commerce_group", class_com, None, "last 12")
    populate_table("commerce_group", "commerce_expense", "1401", "1401", "group_name", "expense", "id_commerce_group", class_com, None, "last 12")

def populate_all_industry():
    """Populate all industry tables."""
    populate_segment_type_table("industrial_activity", "activity")
    populate_segment_type_table("industrial_activity_CNAE", "activity")
    populate_table("industrial_activity", "industrial_production", "8888", "12607", "activity", "production", "id_activity", class_in, None, "last 60")
    populate_table("industrial_activity_CNAE", "industrial_revenue", "1853", "805", "activity", "revenue", "id_activity_CNAE", class_in_CNAE, None, "last 12")

def populate_all_service():
    """Populate all service tables."""
    populate_segment_type_table("service_segment", "service")
    populate_table("service_segment", "service_volume", "8163", "7168", "service", "volume", "id_service", None, class_s_v, "last 60")
    populate_table("service_segment", "service_revenue", "8163", "7168", "service", "revenue", "id_service", None, class_s_r, "last 60")
    
    
