"""
Data aggregation module for the New Investment Analyzer project.

The module provides functions to:
- Aggregate commerce data (volume, division, ranking, revenue and expenses)
- Aggregate industry data (production and revenue)
- Aggregate service data (volume and revenue)

Each function connects to PostgreSQL to fetch data and stores results in MongoDB collections.
The data is formatted for visualization in charts and time series analysis.
"""
import logging
import models
import re
import unicodedata

from collections import defaultdict
from db.db import get_mongo_db, get_db_connection

logger = logging.getLogger(__name__)

def aggregate(data: models.PopulateOutput) -> models.AggregateOutput:
    """
    Main aggregation function that processes all data sectors.

    Args:
        data: PopulateOutput object containing all populated data tables

    Returns:
        AggregateOutput object containing all aggregated data ready for visualization
    """
    try:
        commerce_volume = aggregate_commerce_volume(data.commerce)
        commerce_division = aggregate_commerce_division(data.commerce)
        commerce_ranking = aggregate_commerce_ranking(data.commerce)
        commerce_revenue_expense = aggregate_commerce_revenue_expense_year(data.commerce)
        commerce_revenue_expense_grouped = aggregate_commerce_revenue_expense_grouped(data.commerce)

        industry_production = aggregate_industry_production(data.industry)
        industry_revenue_yearly = aggregate_industry_revenue_yearly(data.industry)

        service_volume_monthly = aggregate_service_volume_monthly(data.service)
        service_volume_ranking = aggregate_service_volume_ranking(data.service)
        service_revenue_monthly = aggregate_service_revenue_monthly(data.service)
        service_revenue_ranking = aggregate_service_revenue_ranking(data.service)

        commerce = models.CommerceAggregate(
            volume=commerce_volume,
            division=commerce_division,
            ranking=commerce_ranking,
            revenue_expense=commerce_revenue_expense,
            revenue_expense_grouped=commerce_revenue_expense_grouped
        )
        industry = models.IndustryAggregate(
            production=industry_production,
            revenue_yearly=industry_revenue_yearly
        )
        service = models.ServiceAggregate(
            volume=service_volume_monthly,
            volume_ranking=service_volume_ranking,
            revenue=service_revenue_monthly,
            revenue_ranking=service_revenue_ranking
        )
        return models.AggregateOutput(
            commerce=commerce,
            industry=industry,
            service=service
        )
    except Exception as e:
        logger.error(f"Error in main aggregation process: {str(e)}")
        raise

def aggregate_commerce_volume(data: models.CommercePopulate) -> str:
    """
    Aggregates commerce volume data into a time series.

    Args:
        data: CommercePopulate object containing commerce tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    table_name = data.volume_table
    query = f"""
        SELECT date, sum(volume) as volume
        FROM {table_name}
        GROUP BY date
        ORDER BY date;
    """
    try:
        collection_name = "commerce_volume"
        mongodb = get_mongo_db()

        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                for row in rows:
                    date = row[0]
                    value = float(row[1])

                    doc = {
                        "date": date, "value": value
                    }
                    mongodb.get_default_database().get_collection(collection_name).update_one(
                        {"_id": date},
                        {"$set": doc},
                        upsert=True
                    )
             
                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing commerce volume data in MongoDB: {str(e)}")
        raise

def aggregate_commerce_division(data: models.CommercePopulate) -> str:
    """
    Aggregates commerce volume data by division.

    Args:
        data: CommercePopulate object containing commerce tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    table_name = data.volume_table
    group_table = data.group_table
    collection_name = "commerce_division"
    mongodb = get_mongo_db()

    query = f"""
        SELECT cg.type, cv.date, SUM(cv.volume) as total_volume
        FROM {table_name} cv
        JOIN {group_table} cg ON cv.id_commerce_group = cg.id
        GROUP BY cg.type, cv.date
        ORDER BY cv.date, cg.type;
    """
    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                def get_division_name(type_code):
                    if type_code.startswith('2.'):
                        return "vehicle_parts_motorcycle"
                    elif type_code.startswith('3.'):
                        return "wholesale_trade"
                    elif type_code.startswith('4.'):
                        return "retail_trade"
                 
                data_by_date = {}
                
                for row in rows:
                    date = row[1]
                    division_name = get_division_name(row[0])
                    value = float(row[2])
                    
                    if date not in data_by_date:
                        data_by_date[date] = {
                            "vehicle_parts_motorcycle": 0,
                            "wholesale_trade": 0,
                            "retail_trade": 0
                        }
                    
                    if division_name in data_by_date[date]:
                        data_by_date[date][division_name] += value

                for date, division_values in data_by_date.items():
                    data_items = [
                        {
                            "date": date,
                            "name": "vehicle_parts_motorcycle",
                            "value": division_values["vehicle_parts_motorcycle"]
                        },
                        {
                            "date": date,
                            "name": "wholesale_trade",
                            "value": division_values["wholesale_trade"]
                        },
                        {
                            "date": date,
                            "name": "retail_trade",
                            "value": division_values["retail_trade"]
                        }
                    ]
                    
                    doc = {"data": data_items}
                    mongodb.get_default_database().get_collection(collection_name).update_one(
                        {"_id": date}, 
                        {"$set": doc}, 
                        upsert=True
                    )
                
                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing commerce division data in MongoDB: {str(e)}")
        raise

def aggregate_commerce_ranking(data: models.CommercePopulate) -> str:
    """
    Creates a ranking of commerce groups by volume.

    Args:
        data: CommercePopulate object containing commerce tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    table_name = data.volume_table
    group_table = data.group_table
    collection_name = "commerce_ranking"
    mongodb = get_mongo_db()

    query = f"""
        SELECT cg.type, cv.date, cv.volume
        FROM {table_name} cv
        JOIN {group_table} cg ON cv.id_commerce_group = cg.id
        ORDER BY cv.date, cv.volume DESC;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                grouped_data = {}

                for row in rows:
                    date = row[1]
                    division_name = row[0]
                    value = float(row[2])
                    
                    if date not in grouped_data:
                        grouped_data[date] = []
                    
                    grouped_data[date].append(
                        {
                            "date": date,
                            "name": division_name,
                            "value": value
                        }
                    )

                for date, data_items in grouped_data.items():
                    doc = {"data": data_items}
                    mongodb.get_default_database().get_collection(collection_name).update_one(
                        {"_id": date}, 
                        {"$set": doc}, 
                        upsert=True
                    )

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing commerce ranking data in MongoDB: {str(e)}")
        raise

def aggregate_commerce_revenue_expense_year(data: models.CommercePopulate) -> str:
    """
    Aggregates yearly revenue and expenses for commerce sector.

    Args:
        data: CommercePopulate object containing commerce tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    revenue_table = data.revenue_table
    expense_table = data.expense_table
    group_table = data.group_table
    collection_name = "commerce_revenue_expense_year"
    mongodb = get_mongo_db()

    # Revenue query
    revenue_query = f"""
        SELECT cr.date, SUM(cr.revenue) as total_revenue
        FROM {revenue_table} cr
        JOIN {group_table} cg ON cr.id_commerce_group = cg.id
        GROUP BY cr.date
        ORDER BY cr.date;
    """

    # Expense query
    expense_query = f"""
        SELECT ce.date, SUM(ce.expense) as total_expense
        FROM {expense_table} ce
        JOIN {group_table} cg ON ce.id_commerce_group = cg.id
        GROUP BY ce.date
        ORDER BY ce.date;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(revenue_query)
                revenue_rows = cur.fetchall()
                
                cur.execute(expense_query)
                expense_rows = cur.fetchall()
                
                grouped_data = {}

                for row in revenue_rows:
                    date = row[0]
                    name = "revenue"
                    value = float(row[1])

                    item = {
                        "date": date,
                        "name": name,
                        "value": round(value / 1_000_000, 2)
                    }
                    grouped_data.setdefault(date, []).append(item)
                
                for row in expense_rows:
                    date = row[0]
                    name = "expense"
                    value = float(row[1])

                    item = {
                        "date": date,
                        "name": name,
                        "value": round(value / 1_000_000, 2)                     
                    }
                    grouped_data.setdefault(date, []).append(item)
                
                for date, data_items in grouped_data.items():
                    doc = {"data": data_items}
                    mongodb.get_default_database().get_collection(collection_name).update_one(
                        {"_id": date},
                        {"$set": doc},
                        upsert=True
                    )
                
            logger.info(f"Data stored in MongoDB collection: {collection_name}")
            return collection_name
    
    except Exception as e:
        logger.error(f"Error storing commerce revenue/expense data in MongoDB: {str(e)}")
        raise

def aggregate_commerce_revenue_expense_grouped(data: models.CommercePopulate) -> str:
    """
    Aggregates revenue and expenses by commerce division.

    Args:
        data: CommercePopulate object containing commerce tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    revenue_table = data.revenue_table
    expense_table = data.expense_table
    group_table = data.group_table
    collection_name = "commerce_revenue_expense_grouped"
    db = get_mongo_db()

    # Revenue query by division
    revenue_query = f"""
        SELECT cg.type, cr.date, SUM(cr.revenue) as total_revenue
        FROM {revenue_table} cr
        JOIN {group_table} cg ON cr.id_commerce_group = cg.id
        GROUP BY cg.type, cr.date
        ORDER BY cr.date, cg.type;
    """

    # Expense query by division
    expense_query = f"""
        SELECT cg.type, ce.date, SUM(ce.expense) as total_expense
        FROM {expense_table} ce
        JOIN {group_table} cg ON ce.id_commerce_group = cg.id
        GROUP BY cg.type, ce.date
        ORDER BY ce.date, cg.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(revenue_query)
                revenue_results = cur.fetchall()
                
                cur.execute(expense_query)
                expense_results = cur.fetchall()

                def get_division_name(type_code):
                    if type_code.startswith('2.'):
                        return "vehicle_parts_motorcycle"
                    elif type_code.startswith('3.'):
                        return "wholesale_trade"
                    elif type_code.startswith('4.'):
                        return "retail_trade"
                    return "other"

                aggregated_by_date = {}
                
                for row in revenue_results:
                    date = row[1]
                    name = "revenue"
                    type_name = get_division_name(row[0])
                    value = float(row[2])

                    date_data = aggregated_by_date.setdefault(date, {})
                    date_data[(name, type_name)] = date_data.get((name, type_name), 0) + value

                for row in expense_results:
                    date = row[1]
                    name = "expense"
                    type_name = get_division_name(row[0])
                    value = float(row[2])

                    date_data = aggregated_by_date.setdefault(date, {})
                    date_data[(name, type_name)] = date_data.get((name, type_name), 0) + value

                for date, grouped_items in aggregated_by_date.items():
                    data_items = [
                        {
                            "date": date,
                            "name": name,
                            "type": type_name,
                            "value": round(value / 1_000_000, 2)
                        }
                        for (name, type_name), value in grouped_items.items()
                    ]
                    db.get_default_database().get_collection(collection_name).update_one(
                        {"_id": date},
                        {"$set": {"data": data_items}},
                        upsert=True
                    )
                    
                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing commerce revenue/expense grouped data in MongoDB: {str(e)}")
        raise

def aggregate_industry_production(data: models.IndustryPopulate) -> str:
    """
    Aggregates industrial production data by activity type.

    Args:
        data: IndustryPopulate object containing industry tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    activity_table = data.activity_table
    production_table = data.production_table
    mongodb = get_mongo_db()
    collection_name = "industry_production_series"

    query = f"""
        SELECT ia.type, ip.date, ip.production
        FROM {production_table} ip
        JOIN {activity_table} ia ON ip.id_activity = ia.id
        ORDER BY ip.date, ia.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                series_by_activity = {}
                for activity, raw_date, value in rows:
                    match = re.match(r"([a-zç]+)\s+(\d{4})", raw_date.lower())
                    if not match:
                        continue
                    month_str, year = match.groups()

                    month_map = {
                        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                    }
                    month = month_map.get(month_str)
                    if not month:
                        continue

                    date = f"{year}-{month}"

                    if activity not in series_by_activity:
                        series_by_activity[activity] = []
                    
                    series_by_activity[activity].append({
                        "date": date,
                        "value": round(float(value), 2)
                    })

                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for activity in series_by_activity:
                    series_by_activity[activity].sort(key=lambda x: x["date"])

                for activity, records in series_by_activity.items():
                    doc = {
                        "_id": unicodedata.normalize("NFKD", activity).encode("ASCII", "ignore").decode().lower().replace(" ", "_"),
                        "data": records
                    }
                    collection.insert_one(doc) 

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing industry production data in MongoDB: {str(e)}")
        raise

def aggregate_industry_revenue_yearly(data: models.IndustryPopulate) -> str:
    """
    Aggregates yearly revenue by CNAE industrial classification.

    Args:
        data: IndustryPopulate object containing industry tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    activity_cnae_table = data.activity_CNAE_table
    revenue_table = data.revenue_table
    mongodb = get_mongo_db()
    collection_name = "industry_revenue_yearly"

    query = f"""
        SELECT iac.type, ir.date, SUM(ir.revenue) as total_revenue
        FROM {revenue_table} ir
        JOIN {activity_cnae_table} iac ON ir.id_activity_CNAE = iac.id
        GROUP BY iac.type, ir.date
        ORDER BY ir.date, iac.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                data_by_activity = {}
                for activity, date, value in rows:
                    if activity not in data_by_activity:
                        data_by_activity[activity] = []

                    data_by_activity[activity].append({
                        "date": date,
                        "value": round(float(value), 2)
                    })
                    
                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for activity, records in data_by_activity.items():
                    doc = {
                        "_id": unicodedata.normalize("NFKD", activity).encode("ASCII", "ignore").decode().lower().replace(" ", "_"),
                        "data": records
                    }
                    collection.insert_one(doc) 

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing industry revenue data in MongoDB: {str(e)}")
        raise

def aggregate_service_volume_monthly(data: models.ServicePopulate) -> str:
    """
    Aggregates monthly service volume data.

    Args:
        data: ServicePopulate object containing service tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    segment_table = data.segment_table
    volume_table = data.volume_table
    mongodb = get_mongo_db()
    collection_name = "service_volume_monthly"

    query = f"""
        SELECT ss.type, sv.date, sv.volume
        FROM {volume_table} sv
        JOIN {segment_table} ss ON sv.id_service = ss.id
        ORDER BY sv.date, ss.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                series_by_segment = {}
                for segment, raw_date, value in rows:
                    match = re.match(r"([a-zç]+)\s+(\d{4})", raw_date.lower())
                    if not match:
                        continue
                    month_str, year = match.groups()

                    month_map = {
                        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                    }
                    month = month_map.get(month_str)
                    if not month:
                        continue

                    date = f"{year}-{month}"

                    if segment not in series_by_segment:
                        series_by_segment[segment] = []

                    series_by_segment[segment].append({
                        "date": date,
                        "value": round(float(value), 2)
                    })

                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for segment in series_by_segment:
                    series_by_segment[segment].sort(key=lambda x: x["date"])
                
                def is_series_nonzero(series):
                    return any(entry["value"] != 0 for entry in series)

                for segment, records in series_by_segment.items():
                    if not is_series_nonzero(records):
                        continue

                    doc = {
                        "_id": unicodedata.normalize("NFKD", segment).encode("ASCII", "ignore").decode().lower().replace(" ", "_"),
                        "data": records
                    }
                    collection.insert_one(doc)

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing service volume data in MongoDB: {str(e)}")
        raise

def aggregate_service_volume_ranking(data: models.ServicePopulate) -> str:
    """
    Creates a ranking of service segments by volume.

    Args:
        data: ServicePopulate object containing service tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    segment_table = data.segment_table
    volume_table = data.volume_table
    mongodb = get_mongo_db()
    collection_name = "service_volume_ranking"

    query = f"""
        SELECT ss.type, sv.date, sv.volume
        FROM {volume_table} sv
        JOIN {segment_table} ss ON sv.id_service = ss.id
        ORDER BY sv.date, ss.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                volumes = defaultdict(lambda: defaultdict(float))

                for segment, raw_date, value in rows:
                    match = re.match(r"([a-zç]+)\s+(\d{4})", raw_date.lower())
                    if not match:
                        continue
                    _, year = match.groups()

                    volumes[segment][year] += float(value)

                def is_nonzero_series(yearly_values):
                    return any(v != 0 for v in yearly_values.values())
                
                filtered_segments = {
                    segment: years
                    for segment, years in volumes.items()
                    if is_nonzero_series(years)
                }

                yearly_data = defaultdict(list)
                for segment, yearly_values in filtered_segments.items():
                    norm_segment = unicodedata.normalize("NFKD", segment).encode("ASCII", "ignore").decode().lower().replace(" ", "_")
                    for year, total in yearly_values.items():
                        yearly_data[year].append({
                            "name": norm_segment,
                            "value": round(total, 2)
                        })
                
                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for year, records in yearly_data.items():
                    doc = {
                        "_id": year,
                        "data": records
                    }
                    collection.insert_one(doc)

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name

    except Exception as e:
        logger.error(f"Error storing service volume ranking data in MongoDB: {str(e)}")
        raise

def aggregate_service_revenue_monthly(data: models.ServicePopulate) -> str:
    """
    Aggregates monthly service revenue data.

    Args:
        data: ServicePopulate object containing service tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    segment_table = data.segment_table
    revenue_table = data.revenue_table
    mongodb = get_mongo_db()
    collection_name = "service_revenue_monthly"

    query = f"""
        SELECT ss.type, sr.date, sr.revenue
        FROM {revenue_table} sr
        JOIN {segment_table} ss ON sr.id_service = ss.id
        ORDER BY sr.date, ss.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                series_by_segment = {}
                for segment, raw_date, value in rows:
                    match = re.match(r"([a-zç]+)\s+(\d{4})", raw_date.lower())
                    if not match:
                        continue
                    month_str, year = match.groups()

                    month_map = {
                        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
                    }
                    month = month_map.get(month_str)
                    if not month:
                        continue

                    date = f"{year}-{month}"

                    if segment not in series_by_segment:
                        series_by_segment[segment] = []

                    series_by_segment[segment].append({
                        "date": date,
                        "value": round(float(value), 2)
                    })

                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for segment in series_by_segment:
                    series_by_segment[segment].sort(key=lambda x: x["date"])
                    
                def is_series_nonzero(series):
                    return any(entry["value"] != 0 for entry in series)

                for segment, records in series_by_segment.items():
                    if not is_series_nonzero(records):
                        continue

                    doc = {
                        "_id": unicodedata.normalize("NFKD", segment).encode("ASCII", "ignore").decode().lower().replace(" ", "_"),
                        "data": records
                    }
                    collection.insert_one(doc)

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing service revenue data in MongoDB: {str(e)}")
        raise

def aggregate_service_revenue_ranking(data: models.ServicePopulate) -> str:
    """
    Creates a ranking of service segments by revenue.

    Args:
        data: ServicePopulate object containing service tables

    Returns:
        str: Name of the MongoDB collection where the data was stored
    """
    segment_table = data.segment_table
    revenue_table = data.revenue_table
    mongodb = get_mongo_db()
    collection_name = "service_revenue_ranking"

    query = f"""
        SELECT ss.type, sr.date, sr.revenue
        FROM {revenue_table} sr
        JOIN {segment_table} ss ON sr.id_service = ss.id
        ORDER BY sr.date, ss.type;
    """

    try:
        with get_db_connection() as postgres_conn:
            with postgres_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                revenues = defaultdict(lambda: defaultdict(float))

                for segment, raw_date, value in rows:
                    match = re.match(r"([a-zç]+)\s+(\d{4})", raw_date.lower())
                    if not match:
                        continue
                    _, year = match.groups()

                    revenues[segment][year] += float(value)

                def is_nonzero_series(yearly_values):
                    return any(v != 0 for v in yearly_values.values())
                
                filtered_segments = {
                    segment: years
                    for segment, years in revenues.items()
                    if is_nonzero_series(years)
                }

                yearly_data = defaultdict(list)
                for segment, yearly_values in filtered_segments.items():
                    norm_segment = unicodedata.normalize("NFKD", segment).encode("ASCII", "ignore").decode().lower().replace(" ", "_")
                    for year, total in yearly_values.items():
                        yearly_data[year].append({
                            "name": norm_segment,
                            "value": round(total, 2)
                        })
                
                collection = mongodb.get_default_database().get_collection(collection_name)
                collection.delete_many({})

                for year, records in yearly_data.items():
                    doc = {
                        "_id": year,
                        "data": records
                    }
                    collection.insert_one(doc)

                logger.info(f"Data stored in MongoDB collection: {collection_name}")
                return collection_name
    
    except Exception as e:
        logger.error(f"Error storing service revenue ranking data in MongoDB: {str(e)}")
        raise