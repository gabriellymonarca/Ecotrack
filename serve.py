"""
Web server module for the Ecotrack project.

This module provides:
- Flask web server setup and configuration
- Page routes for rendering HTML templates
- API routes for serving data from MongoDB collections
- Data initialization and server startup functionality
"""
import logging

from db.db import get_mongo_db
from flask import Flask, render_template, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store application data
app_data = None

@app.before_request
def before_request():
    """Initialize necessary data before each request."""
    if app_data is None:
        logger.warning("Application data not initialized. Use serve() function first.")
        return jsonify({"error": "Data not initialized"}), 500

# --------------------- Page routes -----------------------------------
@app.route("/")
def home():
    """Main route that renders the application."""
    logger.info("Accessing route /")
    return render_template("index.html")

@app.route("/commerce")
def commerce():
    """Route that renders the commerce page."""
    logger.info("Accessing route /commerce")
    return render_template("commerce.html")

@app.route("/industry")
def industry():
    """Route that renders the industry page."""
    logger.info("Accessing route /industry")
    return render_template("industry.html")

@app.route("/service")
def service():
    """Route that renders the service page."""
    logger.info("Accessing route /service")
    return render_template("service.html")

# --------------------- Commerce API routes ------------------------------
@app.route("/api/commerce/volume/series")
def get_commerce_volume_series():
    """API route that returns commerce volume data."""
    try:
        collection_name = app_data.commerce.volume
        
        logger.info("Accessing route /api/commerce/volume/series")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify(
            [
                {
                **doc,
                '_id': str(doc['_id'])
                } for doc in docs
            ]
        )
    except Exception as e:
        logger.error(f"Error fetching commerce volume series: {str(e)}")
        return jsonify({"error": "Failed to fetch commerce volume data"}), 500

@app.route("/api/commerce/division")
def get_commerce_division():
    """API route that returns commerce division data."""
    try:
        collection_name = app_data.commerce.division
        
        logger.info("Accessing route /api/commerce/division")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify(
            [
                {
                **doc,
                '_id': str(doc['_id'])
                } for doc in docs
            ]
        )
    except Exception as e:
        logger.error(f"Error fetching commerce division data: {str(e)}")
        return jsonify({"error": "Failed to fetch commerce division data"}), 500

@app.route("/api/commerce/ranking")
def get_commerce_ranking():
    """API route that returns commerce ranking data."""
    try:
        collection_name = app_data.commerce.ranking
        
        logger.info("Accessing route /api/commerce/ranking")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching commerce ranking data: {str(e)}")
        return jsonify({"error": "Failed to fetch commerce ranking data"}), 500

@app.route("/api/commerce/revenue-expense/series")
def get_commerce_revenue_expense_series():
    """API route that returns commerce revenue and expense series data."""
    try:
        collection_name = app_data.commerce.revenue_expense
        
        logger.info("Accessing route /api/commerce/revenue-expense/series")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching commerce revenue/expense series: {str(e)}")
        return jsonify({"error": "Failed to fetch commerce revenue/expense data"}), 500

@app.route("/api/commerce/revenue-expense/grouped")
def get_commerce_revenue_expense_grouped():
    """API route that returns commerce revenue and expense grouped data."""
    try:
        collection_name = app_data.commerce.revenue_expense_grouped
        
        logger.info("Accessing route /api/commerce/revenue-expense/grouped")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching commerce revenue/expense grouped data: {str(e)}")
        return jsonify({"error": "Failed to fetch commerce revenue/expense grouped data"}), 500

# --------------------- Industry API routes ------------------------------
@app.route("/api/industry/production/series")
def get_industry_production_series():
    """API route that returns industry production series data."""
    try:
        collection_name = app_data.industry.production
        
        logger.info("Accessing route /api/industry/production/series")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching industry production series: {str(e)}")
        return jsonify({"error": "Failed to fetch industry production data"}), 500

@app.route("/api/industry/revenue/yearly")
def get_industry_revenue_yearly():
    """API route that returns industry yearly revenue data."""
    try:
        collection_name = app_data.industry.revenue_yearly
        
        logger.info("Accessing route /api/industry/revenue/yearly")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching industry yearly revenue: {str(e)}")
        return jsonify({"error": "Failed to fetch industry revenue data"}), 500

# --------------------- Service API routes ------------------------------
@app.route("/api/service/volume/monthly")
def get_service_volume_monthly():
    """API route that returns service monthly volume data."""
    try:
        collection_name = app_data.service.volume
        
        logger.info("Accessing route /api/service/volume/monthly")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching service monthly volume: {str(e)}")
        return jsonify({"error": "Failed to fetch service volume data"}), 500

@app.route("/api/service/volume/ranking")
def get_service_volume_ranking():
    """API route that returns service volume ranking data."""
    try:
        collection_name = app_data.service.volume_ranking
        
        logger.info("Accessing route /api/service/volume/ranking")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching service volume ranking: {str(e)}")
        return jsonify({"error": "Failed to fetch service volume ranking data"}), 500

@app.route("/api/service/revenue/monthly")
def get_service_revenue_monthly():
    """API route that returns service monthly revenue data."""
    try:
        collection_name = app_data.service.revenue
        
        logger.info("Accessing route /api/service/revenue/monthly")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching service monthly revenue: {str(e)}")
        return jsonify({"error": "Failed to fetch service revenue data"}), 500

@app.route("/api/service/revenue/ranking")
def get_service_revenue_ranking():
    """API route that returns service revenue ranking data."""
    try:
        collection_name = app_data.service.revenue_ranking
        
        logger.info("Accessing route /api/service/revenue/ranking")
        
        db = get_mongo_db()
        docs = db.get_default_database().get_collection(collection_name).find({})
        return jsonify([{
            **doc,
            '_id': str(doc['_id'])
        } for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching service revenue ranking: {str(e)}")
        return jsonify({"error": "Failed to fetch service revenue ranking data"}), 500

def serve():
    """Initialize application data and start the server."""
    try:
        app.run(debug=False)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise