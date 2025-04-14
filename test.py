import logging
from db import get_db_connection
from init_mongo import get_mongo_db

def _execute_query(cursor, query, params=None):
    """Executes a SQL query and returns the results."""
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

def commerce_volume_yearly():
    """Aggregates yearly commerce volume into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT CAST(SUBSTRING(date FROM '[0-9]{4}') AS INTEGER) AS ano, SUM(count)
                    FROM commerce_company_count
                    GROUP BY ano ORDER BY ano;
                """
                rows = _execute_query(cur, query)

        yearly_commerce_volume = {}

        for year, total_count in rows:
            year_str = str(year)
            total_count_float = float(total_count)
            yearly_commerce_volume[year_str] = total_count_float        
        
        collection_name = "tester_collection"
        data = [
            {
                "date": year,
                "value": value
            }
            for year, value in yearly_commerce_volume.items()
        ]
        
        _store_data_in_mongodb(
            collection_name,
            data,                     
        )

    except Exception as e:
        logging.error(f"Error aggregating yearly commerce volume data: {e}")
        raise e
    
def _store_data_in_mongodb(collection_name,query_filter, data, upsert=True):
    """Stores data in MongoDB."""
    db = get_mongo_db()
    collection = db[collection_name]
    collection.update_one(query_filter, {"$set": data}, upsert=upsert)
    logging.info(f"Data stored in MongoDB collection: {collection_name}")