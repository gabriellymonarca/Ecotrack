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

def _store_data_in_mongodb(collection_name, query_filter, data, upsert=True):
    """Stores data in MongoDB."""
    db = get_mongo_db()
    collection = db[collection_name]
    collection.update_one(query_filter, {"$set": data}, upsert=upsert)
    logging.info(f"Data stored in MongoDB collection: {collection_name}")

# ------------------------------- Commerce division collections ----------------------------------- #

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
        
        collection_name = "commerce_volume_yearly"
        category = "commerce"
        suptype = None
        frequency = "yearly"
        unit = "commerce volume"
        series = [
            {
                "date": yearly_commerce_volume[year_str],
                "value": yearly_commerce_volume
            }
        ]
                
        _store_data_in_mongodb("commerce_volume_yearly", {}, {"data": yearly_commerce_volume})

    except Exception as e:
        logging.error(f"Error aggregating yearly commerce volume data: {e}")
        raise e

def commerce_division(year):
    """Aggregates annual commerce division into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                group_query = """
                    SELECT id, group_name FROM commerce_group
                    WHERE group_name SIMILAR TO '2.[1-3]%' OR group_name SIMILAR TO '3.[1-8]%' OR group_name SIMILAR TO '4.[1-8]%';
                """
                result_group = _execute_query(cur, group_query)

                count_query = "SELECT id_commerce_group, count FROM commerce_company_count WHERE date = %s;"
                result_count = _execute_query(cur, count_query, (year,))

        divisions = {
            "vehicle_parts_motorcycle": [id for id, group_name in result_group if group_name.startswith("2.")],
            "wholesale_trade": [id for id, group_name in result_group if group_name.startswith("3.")],
            "retail_trade": [id for id, group_name in result_group if group_name.startswith("4.")],
        }

        commerce_division_data = {
            "vehicle_parts_motorcycle": int(sum(count for id_commerce_group, count in result_count if id_commerce_group in divisions["vehicle_parts_motorcycle"])),
            "wholesale_trade": int(sum(count for id_commerce_group, count in result_count if id_commerce_group in divisions["wholesale_trade"])),
            "retail_trade": int(sum(count for id_commerce_group, count in result_count if id_commerce_group in divisions["retail_trade"])),
            "year": year,
        }

        _store_data_in_mongodb("commerce_division", {"year": year}, commerce_division_data)
        return commerce_division_data

    except Exception as e:
        logging.error(f"Error aggregating commerce division data: {e}")
        raise e

def commerce_ranking(year):
    """Aggregates commerce group activities ranking by divisions into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                group_query = "SELECT id, group_name FROM commerce_group;"
                group_names = {id: name for id, name in _execute_query(cur, group_query)}

                count_query = "SELECT id_commerce_group, count FROM commerce_company_count WHERE date = %s;"
                result_count = _execute_query(cur, count_query, (year,))

        division_counts = {
            "vehicle_parts_motorcycle": {},
            "wholesale_trade": {},
            "retail_trade": {},
        }

        for id_commerce_group, count in result_count:
            group_name = group_names.get(id_commerce_group)
            if group_name:
                if group_name.startswith("2."):
                    division_counts["vehicle_parts_motorcycle"][group_name] = division_counts["vehicle_parts_motorcycle"].get(group_name, 0) + count
                elif group_name.startswith("3."):
                    division_counts["wholesale_trade"][group_name] = division_counts["wholesale_trade"].get(group_name, 0) + count
                elif group_name.startswith("4."):
                    division_counts["retail_trade"][group_name] = division_counts["retail_trade"].get(group_name, 0) + count

        ranking_data = {
            "year": year,
            "vehicle_parts_motorcycle": [{"name": k, "count": float(v)} for k, v in sorted(division_counts["vehicle_parts_motorcycle"].items(), key=lambda x: x[1], reverse=True)[:3]],
            "wholesale_trade": [{"name": k, "count": float(v)} for k, v in sorted(division_counts["wholesale_trade"].items(), key=lambda x: x[1], reverse=True)[:3]],
            "retail_trade": [{"name": k, "count": float(v)} for k, v in sorted(division_counts["retail_trade"].items(), key=lambda x: x[1], reverse=True)[:3]],
        }

        _store_data_in_mongodb("commerce_ranking", {"year": year}, ranking_data)

    except Exception as e:
        logging.error(f"Error aggregating commerce ranking data: {e}")
        raise e

def commerce_revenue_expense_yearly():
    """Aggregates yearly commerce revenue and expense into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                revenue_query = "SELECT CAST(SUBSTRING(date FROM '[0-9]{4}') AS INTEGER) AS ano, SUM(revenue) FROM commerce_revenue GROUP BY ano ORDER BY ano;"
                expense_query = "SELECT CAST(SUBSTRING(date FROM '[0-9]{4}') AS INTEGER) AS ano, SUM(expense) FROM commerce_expense GROUP BY ano ORDER BY ano;"

                revenue_data = {str(year): float(revenue) for year, revenue in _execute_query(cur, revenue_query)}
                expense_data = {str(year): float(expense) for year, expense in _execute_query(cur, expense_query)}

        yearly_data = {"revenue": revenue_data, "expense": expense_data}
        _store_data_in_mongodb("commerce_revenue_expense_yearly", {}, yearly_data)

    except Exception as e:
        logging.error(f"Error aggregating yearly commerce revenue and expense data: {e}")
        raise e

def commerce_revenue_expense_grouped(year):
    """Aggregates commerce revenue and expense grouped by division into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                group_query = "SELECT id, group_name FROM commerce_group;"
                group_names = {id: name for id, name in _execute_query(cur, group_query)}

                revenue_query = "SELECT id_commerce_group, revenue FROM commerce_revenue WHERE date = %s;"
                revenue_data = {group_names[id_commerce_group]: revenue for id_commerce_group, revenue in _execute_query(cur, revenue_query, (year,)) if id_commerce_group in group_names}

                expense_query = "SELECT id_commerce_group, expense FROM commerce_expense WHERE date = %s;"
                expense_data = {group_names[id_commerce_group]: expense for id_commerce_group, expense in _execute_query(cur, expense_query, (year,)) if id_commerce_group in group_names}

        aggregated_data = {
            "vehicle parts motorcycle": {"revenue": 0, "expense": 0},
            "wholesale trade": {"revenue": 0, "expense": 0},
            "retail trade": {"revenue": 0, "expense": 0},
        }

        for area, revenue in revenue_data.items():
            if area.startswith("2."):
                aggregated_data["vehicle parts motorcycle"]["revenue"] += float(revenue)
            elif area.startswith("3."):
                aggregated_data["wholesale trade"]["revenue"] += float(revenue)
            elif area.startswith("4."):
                aggregated_data["retail trade"]["revenue"] += float(revenue)

        for area, expense in expense_data.items():
            if area.startswith("2."):
                aggregated_data["vehicle parts motorcycle"]["expense"] += float(expense)
            elif area.startswith("3."):
                aggregated_data["wholesale trade"]["expense"] += float(expense)
            elif area.startswith("4."):
                aggregated_data["retail trade"]["expense"] += float(expense)

        data = [{"area": category, "revenue": data["revenue"], "expense": data["expense"]} for category, data in aggregated_data.items()]

        document = {"year": year, "data": data}
        _store_data_in_mongodb("commerce_revenue_expense_grouped", {"year": year}, document)

    except Exception as e:
        logging.error(f"Error storing commerce revenue and expense data: {e}")
        raise e

    
# ------------------------------- Industry division collections ------------------------------------------ #

def industrial_production_series(year, activity):
    """Aggregates national industrial production data into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                activity_query = """
                    SELECT id FROM industrial_activity
                    WHERE activity =%s;
                    """
                result_activity = _execute_query(cur, activity_query, (activity,))

                if not result_activity:
                    logging.warning(f"Activity '{activity}' not found.")
                    return
                
                activity_id = result_activity[0][0]

                production_query = """
                    SELECT date, production FROM industrial_production
                    WHERE date LIKE %s
                    AND id_activity =%s
                    ORDER BY date;
                """
                result_production = _execute_query(cur, production_query, (f"%{year}", activity_id))

                industrial_production_data = {
                    "date": year,
                    "activity": activity,
                    "total_production": [
                        {"date": row[0], "production": float(row[1]) if row[1] is not None else 0.0}
                        for row in result_production
                    ]
                }

                _store_data_in_mongodb(
                    "industrial_production_series", 
                    {"year": year, "activity": activity}, 
                    industrial_production_data
                )

    except Exception as e:
        logging.error(f"Error aggregatting industrial production data: {e}")
        raise e
    
def industrial_revenue_yearly(activity):
    """Aggregates industrial production data for a cartogram into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                activity_query = """
                    SELECT id FROM industrial_activity_cnae
                    WHERE activity = %s;
                """
                result_activity = _execute_query(cur, activity_query, (activity,))
                activity_id = result_activity[0][0] 

                revenue_query = """
                    SELECT CAST(SUBSTRING(date FROM '[0-9]{4}') AS INTEGER) AS date, SUM(revenue)
                    FROM industrial_revenue
                    WHERE id_activity_cnae = %s
                    GROUP BY date ORDER BY date;
                """
                result_revenue = _execute_query(cur, revenue_query, (activity_id,))

        revenue_data = {str(year): float(revenue) for year, revenue in result_revenue}

        industrial_revenue_doc = {
            "activity": activity,
            "data": revenue_data
        }

        _store_data_in_mongodb("industrial_revenue_yearly", {"activity": activity}, industrial_revenue_doc)

    except Exception as e:
        logging.error(f"Erro na agregação de dados de receita anual de indústria: {e}")
        raise e

# ------------------------------- Service division collections ------------------------------------------ #

def service_volume_monthly(year, service_segment):
    """Aggregates service volume data into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                segment_query = """
                    SELECT id FROM service_segment
                    WHERE service =%s;
                    """
                result_service = _execute_query(cur, segment_query, (service_segment,))

                if not result_service:
                    logging.warning(f"Service '{service_segment}' not found.")
                    return
                
                service_id = result_service[0][0]

                service_volume_query = """
                    SELECT date, volume FROM service_volume
                    WHERE date LIKE %s
                    AND id_service = %s
                    ORDER BY date;
                """
                result_volume = _execute_query(cur, service_volume_query, (f"%{year}%", service_id))
                
                service_volume_data = {
                    "year": year,
                    "service": service_segment,
                    "monthly_data": [
                        {"date": row[0], "volume": float(row[1]) if row[1] is not None else 0.0}
                        for row in result_volume
                    ]
                }

                _store_data_in_mongodb(
                    "service_volume_monthly", 
                    {"year": year, "service": service_segment}, 
                    service_volume_data
                )

    except Exception as e:
        logging.error(f"Error aggregatting service volume data: {e}")
        raise e

def service_volume_ranking(year, top_n):
    """Aggregates service ranking data into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                ranking_query = """
                    SELECT ss.service, SUM(sv.volume) AS total_volume
                    FROM service_volume sv
                    JOIN service_segment ss ON sv.id_service = ss.id
                    WHERE sv.date LIKE %s
                    GROUP BY ss.service
                    ORDER BY total_volume DESC
                    LIMIT %s;
                    """
                result_ranking = _execute_query(cur, ranking_query, (f"%{year}%", top_n))

                if not result_ranking:
                    logging.warning(f"No ranking data found for {year}.")
                    return

                # Criar estrutura para MongoDB
                service_ranking_data = {
                    "year": year,
                    "top_n": top_n,
                    "ranking": [
                        {"service": row[0], "total_volume": float(row[1])}
                        for row in result_ranking
                    ]
                }

                # Armazena no MongoDB
                _store_data_in_mongodb(
                    "service_volume_ranking",
                    {"year": year, "top_n": top_n},
                    service_ranking_data
                )

    except Exception as e:
        logging.error(f"Error aggregating service ranking data: {e}")
        raise e
    
def service_revenue_monthly(year, service_segment):
    """Aggregates service volume data into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                segment_query = """
                    SELECT id FROM service_segment
                    WHERE service =%s;
                    """
                result_service = _execute_query(cur, segment_query, (service_segment,))

                if not result_service:
                    logging.warning(f"Service '{service_segment}' not found.")
                    return
                
                service_id = result_service[0][0]

                service_revenue_query = """
                    SELECT date, revenue FROM service_revenue
                    WHERE date LIKE %s
                    AND id_service = %s
                    ORDER BY date;
                """
                result_revenue = _execute_query(cur, service_revenue_query, (f"%{year}%", service_id))

                if not result_revenue:
                    logging.warning(f"No revenue data found for service '{service_segment}' in {year}.")
                    return
                
                service_revenue_data = {
                    "year": year,
                    "service": service_segment,
                    "monthly_data": [
                        {"date": row[0], "revenue": float(row[1]) if row[1] is not None else 0.0}
                        for row in result_revenue
                    ]
                }

                _store_data_in_mongodb(
                    "service_revenue_monthly", 
                    {"year": year, "service": service_segment}, 
                    service_revenue_data
                )

    except Exception as e:
        logging.error(f"Error aggregatting revenue data for service: {e}")
        raise e

def service_revenue_ranking(year, top_n):
    """Aggregates service ranking data into MongoDB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                
                ranking_query = """
                    SELECT ss.service, SUM(sr.revenue) AS total_revenue
                    FROM service_revenue sr
                    JOIN service_segment ss ON sr.id_service = ss.id
                    WHERE sr.date LIKE %s
                    GROUP BY ss.service
                    ORDER BY total_revenue DESC
                    LIMIT %s;
                    """
                result_ranking = _execute_query(cur, ranking_query, (f"%{year}%", int(top_n)))

                if not result_ranking:
                    logging.warning(f"No revenue data found for segment service ranking in {year}.")
                    return

                service_ranking_data = {
                    "year": year,
                    "top_n": int(top_n),
                    "ranking": [
                        {"service": row[0], "total_revenue": float(row[1])}
                        for row in result_ranking
                    ]
                }

                _store_data_in_mongodb(
                    "service_revenue_ranking",
                    {"year": year, "top_n": int(top_n)},
                    service_ranking_data
                )

    except Exception as e:
        logging.error(f"Error aggregating revenue data for service segment ranking: {e}")
        raise e

# ------------------------------- Calls to all aggreggation functions ----------------------------------- #
def aggregate_all_commerce(year=None):
    """Aggregates all commerce data into MongoDB.
    
    Args:
        year (str, optional): Ano específico para agregação. Se não fornecido,
                             executa todas as análises disponíveis.
    """
    try:
        # Funções que não dependem de ano específico
        commerce_volume_yearly()
        commerce_revenue_expense_yearly()

        # Se um ano específico foi fornecido, executa as análises dependentes de ano
        if year:
            commerce_division(year)
            commerce_ranking(year)
            commerce_revenue_expense_grouped(year)
            logging.info(f"Dados de comércio agregados com sucesso para o ano {year}.")
        else:
            # Se nenhum ano foi fornecido, executa para todos os anos disponíveis
            # (implementação futura se necessário)
            logging.info("Dados de comércio agregados com sucesso para todos os anos disponíveis.")

    except Exception as e:
        logging.error(f"Erro ao agregar dados de comércio: {e}")
        raise e
    
def aggregate_all_industry(year=None, activity=None):
    try:
        if year and activity:
            industrial_production_series(year, activity)
            logging.info(f"Dados de produção industrial agregados com sucesso para o ano {year} e atividade {activity}.")
        elif activity:
            industrial_revenue_yearly(activity)
            logging.info(f"Dados de receita industrial agregados com sucesso para a atividade {activity}.")
        else:
            logging.info("Dados de indústria agregados com sucesso para todos os anos e atividades disponíveis.")
            
    except Exception as e:
        logging.error(f"Erro ao agregar dados de indústria: {e}")
        raise e
    
def aggregate_all_service(year=None, service_segment=None, top_n=None):
    try:
        service_volume_monthly(year, service_segment)
        service_volume_ranking(year, top_n)
        service_revenue_monthly(year, service_segment)
        service_revenue_ranking(year, top_n)

    except Exception as e:
        logging.error(f"Erro ao agregar todos os dados de serviço: {e}")
        raise e