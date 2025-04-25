# New Investment Analyzer

A comprehensive investment analysis system that collects, processes, and presents Brazilian economic data, focusing on commerce, industry, and services sectors.

## Description

The New Investment Analyzer is a web application that automates the collection and analysis of Brazilian economic data using the SIDRA API (IBGE's Automatic Data Retrieval System). The system processes data from three main sectors:

- **Commerce**: Analysis of volume, revenue, and expenses
- **Industry**: Industrial activity, production, and revenue
- **Services**: Volume and revenue by segment

## System Requirements

- Python 3.8+
- MongoDB
- Modern web browser

## Main Dependencies

- Flask (Web framework)
- pandas (Data manipulation)
- sidrapy (IBGE API)
- pymongo (MongoDB connection)
- APScheduler (Task scheduling)

## Installation

1. Clone the repository:
```bash
git clone [REPOSITORY_URL]
cd New-Investment-Analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# or
.\env\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure MongoDB:
- Ensure MongoDB is installed and running
- Connection settings are located in `db/db.py`

## Usage

1. Start the application:
```bash
python run.py
```

2. Access the web interface:
- Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
New-Investment-Analyzer/
├── run.py              # Application entry point
├── fetch.py            # IBGE data collection
├── populate.py         # Database population
├── aggregate.py        # Data aggregation and analysis
├── serve.py            # Web server and APIs
├── models.py           # Data models
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS)
└── db/                # Database configuration
```

## Main APIs

### Commerce
- `/api/commerce/volume/series` - Volume time series
- `/api/commerce/division` - Sector division
- `/api/commerce/ranking` - Performance ranking
- `/api/commerce/revenue-expense/series` - Revenue and expense series

### Industry
- `/api/industry/production/series` - Production series
- `/api/industry/revenue/yearly` - Annual revenue

### Services
- `/api/service/volume/monthly` - Monthly volume
- `/api/service/revenue/monthly` - Monthly revenue
- `/api/service/volume/ranking` - Volume ranking
- `/api/service/revenue/ranking` - Revenue ranking

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code style
- Keep documentation up to date
- Write tests for new features

## Credits

- Data provided by [IBGE](https://www.ibge.gov.br/)
- Developed by [Gabrielly Monarca/as a Harvard CS50 final project]

## Additional Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [SIDRA API Documentation](https://api.sidra.ibge.gov.br/)
