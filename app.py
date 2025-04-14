from flask import Flask, render_template, jsonify, request
from db import get_db_connection
from init_mongo import get_mongo_db

import logging
import json
from bson import ObjectId

# Scheduled tasks management
from apscheduler.schedulers.background import BackgroundScheduler

# Project modules
from populate import (
    populate_all_commerce, 
    populate_all_industry, 
    populate_all_service
)
from aggregate_mongo import (
    aggregate_all_commerce,
    aggregate_all_industry,
    aggregate_all_service,
    industrial_production_series,
    industrial_revenue_yearly
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Helper function to convert ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId): 
            return str(o)
        return super().default(o)
app.json_encoder = JSONEncoder

# Main route that renders the application
@app.route("/")
def home():
    """Main route that renders the application."""
    logger.info("Acessando rota /")
    return render_template("home.html")

# ---------------------- Page routes -------------------------------------------------------
@app.route("/commerce")
def commerce():
    """Route that renders the commerce page."""
    logger.info("Acessando rota /commerce")
    return render_template("commerce.html")

@app.route("/industry")
def industry():
    """Route that renders the industry page."""
    logger.info("Acessando rota /industry")
    return render_template("industry.html")

@app.route("/service")
def service():
    """Route that renders the service page."""
    logger.info("Acessando rota /service")
    return render_template("service.html")

# ---------------------- Commerce API routes -----------------------------------------------
@app.route("/api/commerce_volume_yearly")
def api_commerce_volume_yearly():
    logger.info("Acessando rota /api/commerce_volume_yearly")
    db = get_mongo_db()
    data = db.commerce_volume_yearly.find()
    return jsonify([{
        **doc,
        '_id': str(doc['_id']) 
    } for doc in data])

@app.route("/api/commerce_division")
def api_commerce_division():
    logger.info("Acessando rota /api/commerce_division")
    db = get_mongo_db()
    data = list(db.commerce_division.find())
    return jsonify([{
        **doc,
        '_id': str(doc['_id'])
    } for doc in data])

@app.route("/api/commerce_ranking")
def api_commerce_ranking():
    logger.info("Acessando rota /api/commerce_ranking")
    db = get_mongo_db()
    data = list(db.commerce_ranking.find())
    return jsonify([{
        **doc,
        '_id': str(doc['_id'])
    } for doc in data])

@app.route("/api/commerce_revenue_expense_yearly")
def api_commerce_revenue_expense_yearly():
    logger.info("Acessando rota /api/commerce_revenue_expense_yearly")
    db = get_mongo_db()
    data = db.commerce_revenue_expense_yearly.find()
    return jsonify([{
        **doc,
        '_id': str(doc['_id'])
    } for doc in data])

@app.route("/api/commerce_revenue_expense_grouped")
def api_commerce_revenue_expense_grouped():
    logger.info("Acessando rota /api/commerce_revenue_expense_grouped")
    db = get_mongo_db()
    data = db.commerce_revenue_expense_grouped.find()
    return jsonify([{
        **doc,
        '_id': str(doc['_id'])
    } for doc in data])

@app.route("/api/service_segment")
def api_service_segment():
    logger.info("Acessando rota /api/service_segment")
    db = get_mongo_db()
    data = list(db.service_segment.find())
    return jsonify([{
        **doc,
        '_id': str(doc['_id'])
    } for doc in data])

# ---------------------- Industry API routes -----------------------------------------------
@app.route("/api/industrial_production_series")
def api_industrial_production_series():
    """API route for industrial production series data."""
    logger.info("Acessando rota /api/industrial_production_series")
    try:
        db = get_mongo_db()
        data = list(db.industrial_production_series.find())
        logger.info(f"Retornando {len(data)} registros de industrial_production_series")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de industrial_production_series: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/industrial_revenue_yearly")
def api_industrial_revenue_yearly():
    """API route for industrial revenue yearly data."""
    logger.info("Acessando rota /api/industrial_revenue_yearly")
    try:
        db = get_mongo_db()
        data = list(db.industrial_revenue_yearly.find())
        logger.info(f"Retornando {len(data)} registros de industrial_revenue_yearly")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de industrial_revenue_yearly: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/industrial_activity")
def api_industrial_activity():
    """API route for industrial activity data from PostgreSQL."""
    logger.info("Acessando rota /api/industrial_activity")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT activity FROM industrial_activity ORDER BY activity")
        activities = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        logger.info(f"Retornando {len(activities)} atividades industriais")
        return jsonify(activities)
    except Exception as e:
        logger.error(f"Erro ao buscar atividades industriais: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/industrial_activity_cnae")
def api_industrial_activity_cnae():
    """API route for industrial activity CNAE data from PostgreSQL."""
    logger.info("Acessando rota /api/industrial_activity_cnae")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT activity FROM industrial_activity_cnae ORDER BY activity")
        activities = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        logger.info(f"Retornando {len(activities)} atividades CNAE")
        return jsonify(activities)
    except Exception as e:
        logger.error(f"Erro ao buscar atividades CNAE: {e}")
        return jsonify({"error": str(e)}), 500

# Novas rotas para gerar dados no MongoDB quando uma atividade for selecionada
@app.route("/api/generate_industrial_production", methods=["POST"])
def api_generate_industrial_production():
    """API route to generate industrial production data for a specific activity and date."""
    logger.info("Acessando rota /api/generate_industrial_production")
    try:
        data = request.json
        activity = data.get("activity")
        date = data.get("date")
        
        if not activity or not date:
            logger.error("Atividade e data são obrigatórios")
            return jsonify({"error": "Atividade e data são obrigatórios"}), 400
            
        logger.info(f"Gerando dados de produção industrial para atividade: {activity} e data: {date}")
        industrial_production_series(date, activity)
        
        # Buscar os dados gerados
        db = get_mongo_db()
        result = db.industrial_production_series.find_one({"activity": activity, "date": date})
        
        if result:
            result["_id"] = str(result["_id"])
            logger.info(f"Dados gerados com sucesso: {result}")
            return jsonify(result)
        else:
            logger.error("Dados não encontrados após geração")
            return jsonify({"error": "Dados não encontrados após geração"}), 404
            
    except Exception as e:
        logger.error(f"Erro ao gerar dados de produção industrial: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate_industrial_revenue", methods=["POST"])
def api_generate_industrial_revenue():
    """API route to generate industrial revenue data for a specific activity."""
    logger.info("Acessando rota /api/generate_industrial_revenue")
    try:
        data = request.json
        activity = data.get("activity")
        
        if not activity:
            logger.error("Atividade é obrigatória")
            return jsonify({"error": "Atividade é obrigatória"}), 400
            
        logger.info(f"Gerando dados de receita industrial para atividade: {activity}")
        industrial_revenue_yearly(activity)
        
        # Buscar os dados gerados
        db = get_mongo_db()
        result = db.industrial_revenue_yearly.find_one({"activity": activity})
        
        if result:
            result["_id"] = str(result["_id"])
            logger.info(f"Dados gerados com sucesso: {result}")
            return jsonify(result)
        else:
            logger.error("Dados não encontrados após geração")
            return jsonify({"error": "Dados não encontrados após geração"}), 404
            
    except Exception as e:
        logger.error(f"Erro ao gerar dados de receita industrial: {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------- Service API routes -----------------------------------------------
@app.route("/api/service_volume_monthly")
def api_service_volume_yearly():
    logger.info("Acessando rota /api/service_volume_monthly")
    try:
        db = get_mongo_db()
        data = list(db.service_volume_monthly.find())
        logger.info(f"Retornando {len(data)} registros de service_volume_monthly")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de service_volume_monthly: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/service_volume_ranking")
def api_service_volume_ranking():
    logger.info("Acessando rota /api/service_volume_ranking")
    try:
        db = get_mongo_db()
        data = list(db.service_volume_ranking.find())
        logger.info(f"Retornando {len(data)} registros de service_volume_ranking")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de service_volume_ranking: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/service_revenue_monthly")
def api_service_revenue_yearly():
    logger.info("Acessando rota /api/service_revenue_monthly")
    try:
        db = get_mongo_db()
        data = list(db.service_revenue_monthly.find())
        logger.info(f"Retornando {len(data)} registros de service_revenue_monthly")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de service_revenue_monthly: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/service_revenue_ranking")
def api_service_revenue_ranking():
    logger.info("Acessando rota /api/service_revenue_ranking")
    try:
        db = get_mongo_db()
        data = list(db.service_revenue_ranking.find())
        logger.info(f"Retornando {len(data)} registros de service_revenue_ranking")
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in data])
    except Exception as e:
        logger.error(f"Erro ao buscar dados de service_revenue_ranking: {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------- functions to periodically update graphs --------------------------

# Functions to populate postgres with sidra data and update mongodb objects every 30 days  
def update_data():
    """Updates SIDRA data and aggregates in MongoDB."""
    try:
        # Populate postgres
        logging.info("Starting SIDRA data update...")
        
        # Try to populate each sector separately
        try:
            populate_all_commerce()
            logging.info("Commerce data updated successfully")
        except Exception as e:
            logging.error(f"Error updating commerce data: {e}")
            
        try:
            populate_all_industry()
            logging.info("Industry data updated successfully")
        except Exception as e:
            logging.error(f"Error updating industry data: {e}")
            
        try:
            populate_all_service()
            logging.info("Service data updated successfully")
        except Exception as e:
            logging.error(f"Error updating service data: {e}")
            
        logging.info("SIDRA data update completed")
        
        # Update mongo
        logging.info("Starting MongoDB data aggregation...")
        
        # Try to aggregate each sector separately
        try:
            aggregate_all_commerce()
            logging.info("Commerce data aggregated successfully")
        except Exception as e:
            logging.error(f"Error aggregating commerce data: {e}")
            
        try:
            aggregate_all_industry()
            logging.info("Industry data aggregated successfully")
        except Exception as e:
            logging.error(f"Error aggregating industry data: {e}")
            
        try:
            aggregate_all_service()
            logging.info("Service data aggregated successfully")
        except Exception as e:
            logging.error(f"Error aggregating service data: {e}")
            
        logging.info("MongoDB data aggregation completed")
        
    except Exception as e:
        logging.error(f"Critical error during data update: {e}")
        raise

if __name__ == "__main__":
    # Imprimir todas as rotas registradas
    print("Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule}")
    
    # Configure scheduler to update data every 30 days
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_data, trigger="interval", days=30)
    scheduler.start()
    
    # Execute initial update
    update_data()
    
    # Start the application
    app.run(debug=True, use_reloader=False)
