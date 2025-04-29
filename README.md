# Ecotrack

Video Demo: [I've finished Harvard's CS50 and THIS is my final project](https://youtu.be/8niTePquiFA?si=5aOR6m8DlRW4qrti)

## Description

Ecotrack is a web application developed to collect, process, store, and visualize Brazilian economic data, with a specific focus on three sectors: commerce, industry, and services. The project was designed to implement a complete data pipeline, providing experience in back-end development, database design, and front-end integration.

The system architecture includes a data ingestion module that extracts datasets from the IBGE's SIDRA API (Sistema IBGE de Recuperação Automática). Retrieved data is transformed and normalized into structured formats suitable for storage in a hybrid database system composed of PostgreSQL and MongoDB. The web application is built with Python (Flask) for the back-end and HTML, CSS, and JavaScript for the front-end, ensuring dynamic interaction with the data.

Automated scripts manage the periodic updating of datasets to maintain data relevance. The modular design of the system separates concerns between data fetching, processing, storage, and visualization, allowing independent development and testing of each component. The project was structured to support future extensions, such as the inclusion of additional economic sectors, new data sources, and more complex analytical tools, following principles of software scalability and maintainability.

## Technical Architecture

The project is structured with a modular architecture that organizes the system into four primary components, each responsible for a specific phase of the data pipeline.

**Data Collection (`fetch.py`)**

The Data Collection component (fetch.py) is responsible for the automated retrieval of raw economic datasets from the IBGE's SIDRA API. It implements a series of specialized functions for each major economic sector—commerce, industry, and services—fetching multiple indicators such as group classifications, production volumes, revenues, and expenses. The module uses the sidrapy library to perform API interactions and pandas for local data manipulation and cleaning.

Data fetching operations are parameterized to support different table structures, classification systems, and time frames, ensuring flexibility and reusability across various datasets. Retrieved datasets undergo a cleaning pipeline that validates essential fields, standardizes date formats, removes unwanted or invalid entries, and normalizes missing or malformed values. Each dataset is transformed into a uniform schema with consistent column names, facilitating subsequent database insertion.

The module incorporates robust error handling and logging mechanisms to detect and report connection issues, invalid API responses, and data inconsistencies. Defensive programming techniques are employed, such as column existence checks and exclusion of non-numeric values, to guarantee that only valid, structured data proceeds through the pipeline. Additionally, security measures are implemented to prevent corrupt or incomplete data from being ingested, ensuring the integrity of the collected information for downstream processing.

**Data Storage (`populate.py`)**

The Data Storage component (populate.py) is responsible for converting the fetched datasets into structured relational database records. It creates all necessary PostgreSQL tables if they do not already exist, ensuring that the database schema remains consistent with the incoming data model. This module handles the insertion of normalized data for three major sectors: commerce, industry, and services, with each sector composed of multiple specialized tables (e.g., volume, revenue, expenses, and groupings). Referential integrity is maintained through foreign key relationships, and data uniqueness is enforced via constraints on primary keys and composite keys.

The component ensures that only validated and complete data are inserted, incorporating logging, exception handling, and defensive programming practices to handle connection errors, constraint violations, and data anomalies. Data insertion operations are idempotent, using ON CONFLICT DO NOTHING clauses to avoid duplicate entries. Additionally, the module includes functionality for dynamically creating tables through parameterized SQL execution and implements robust transaction management to guarantee atomicity and consistency during population processes. The design emphasizes reliability, modularity, and readiness for future expansions or schema changes without requiring major rewrites.

**Data Processing (`aggregate.py`)**

The Data Processing component (aggregate.py) handles the transformation of structured relational data into document-based collections optimized for visualization and analysis. This module reads normalized records from the PostgreSQL database and performs aggregation, ranking, and time series construction for the commerce, industry, and service sectors. The processed datasets are then stored in MongoDB collections, formatted to directly support dynamic charts, rankings, and temporal trend analysis in the frontend application.

Each aggregation function executes specific SQL queries to group, sum, or filter the relational data according to economic activity, division type, or time period (monthly or yearly). The data is then restructured into JSON-compatible formats, often implementing normalization strategies such as converting raw dates into ISO formats and unifying naming conventions using Unicode normalization. The system ensures idempotency by upserting (insert or update) documents based on primary keys such as dates or activity types, maintaining database consistency even under repeated executions.

This module includes extensive error handling, connection management, and transaction safety for both PostgreSQL and MongoDB operations. By isolating aggregation logic into clearly defined functions for each sector and indicator type, the design achieves high modularity and ease of extension. The architecture also implements defensive data validation, ensuring that only non-null, numerically valid records are persisted. The result is a set of MongoDB collections specifically structured to maximize the performance and usability of frontend data visualizations.

**Web Server (`serve.py`)**

The Web Server component (serve.py) provides the HTTP interface between users and the backend data infrastructure of the Ecotrack system. It is built using the Flask microframework and is responsible for both serving static HTML pages and exposing RESTful API endpoints that deliver data from MongoDB collections to the frontend for visualization.

The module implements page routing to render views corresponding to the major economic sectors—commerce, industry, and services—through HTML templates. In parallel, it defines a comprehensive set of API endpoints under a structured namespace, allowing frontend scripts to asynchronously request time series, rankings, and aggregated datasets dynamically. Data returned through the API is serialized into JSON, with proper transformation of internal MongoDB _id fields to maintain compatibility with standard web clients.

Internally, the server maintains a lightweight initialization procedure that validates the readiness of application data before handling requests. The design incorporates error handling at the API level to provide clear responses in case of data access failures, and it logs all request activities for operational traceability. The server structure ensures separation of concerns between routing, data retrieval, and response serialization, facilitating future extensions such as new endpoints or integration of authentication layers. The serve() function encapsulates server startup logic, promoting clean initialization and allowing controlled execution environments.

## Technical Challenges and Solutions

Throughout the development of the Ecotrack project, several technical challenges were encountered and addressed systematically.

1. **Database Integration**: A key architectural decision was to integrate two distinct database systems—PostgreSQL and MongoDB—within a unified data pipeline. PostgreSQL was used to store structured, relational data, while MongoDB served as the primary data source for the frontend due to its flexibility with document-based formats. Custom synchronization mechanisms were developed to maintain consistency between relational and document models. This included standardized data exports, transaction management for critical operations, and automated backup procedures to ensure database resilience and recoverability.

2. **API Integration**: Interfacing with the SIDRA API through the sidrapy library introduced its own set of challenges, mainly due to limited documentation and API inconsistencies. To address this, a flexible data fetching framework was built, supporting different table schemas, classification types, and periods dynamically. Robust error handling and retry logic were implemented to manage network failures and API downtime gracefully. Detailed logging was added to capture and trace all API interactions, enabling faster debugging and improved system observability.

3. **Data Standardization and Frontend Compatibility**: The most significant technical challenge was designing a consistent and predictable data schema suitable for frontend visualization. MongoDB collections had to follow strict formatting rules to ensure compatibility with dynamic JavaScript charting libraries without the need for dataset-specific parsing logic. This involved:

- Defining a uniform data model across all economic sectors, standardizing fields such as date, value, and type.
- Normalizing date formats into ISO-style strings (YYYY-MM) for time series analysis.
- Applying consistent naming conventions for MongoDB collection identifiers and document fields.
- Structuring all time series and rankings with predictable array-based formats to support automated chart generation.
- Implementing rigorous data cleaning, validation, and transformation pipelines before insertion into MongoDB.
- Designing data versioning and update strategies to maintain historical integrity without data duplication.

## Technologies and Libraries

The project utilizes the following technologies and libraries:

### Backend Framework and Web Server

- **Flask**: Web framework for building the REST API and serving web pages
- **Jinja2**: Template engine for rendering HTML pages

### Database Systems

- **PostgreSQL**: Primary relational database for structured data storage
  - psycopg3: PostgreSQL adapter for Python
- **MongoDB**: Document database for flexible data storage and retrieval
  - pymongo: MongoDB driver for Python

### Data Processing and Analysis

- **pandas**: Data manipulation and analysis library
  - Used for data cleaning, transformation, and aggregation
- **sidrapy**: Python wrapper for IBGE's SIDRA API
  - Handles API authentication and data retrieval
- **requests**: HTTP library for API interactions

### Task Scheduling and Automation

- **APScheduler**: Advanced Python Scheduler
  - BackgroundScheduler for automated data updates
  - CronTrigger for scheduling periodic tasks

### Frontend Technologies

- **HTML5/CSS3**: Web standards for structure and styling
- **JavaScript**: Client-side scripting
- **Chart.js**: Interactive charting library for data visualization
- **Bootstrap**: CSS framework for responsive design
- **jQuery**: JavaScript library for DOM manipulation

### Development Tools and Utilities

- **logging**: Python's built-in logging module for system monitoring
- **yaml**: YAML parser for configuration files
- **datetime**: Date and time handling
- **typing**: Type hints for better code documentation

## Project Structure

```bash
Ecotrack/
├── run.py              # Application entry point
├── fetch.py            # IBGE data collection
├── populate.py         # Database population
├── aggregate.py        # Data aggregation and analysis
├── serve.py            # Web server and APIs
├── models.py           # Data models
├── scheduler.py        # Automated data update scheduling
├── requirements.txt    # Project dependencies
├── templates/          # HTML templates
│   ├── index.html      # Main landing page
│   ├── commerce.html   # Commerce sector visualization
│   ├── industry.html   # Industry sector visualization
│   └── service.html    # Service sector visualization
├── static/             # Static files
│   ├── css/            # Stylesheets
│   │   ├── style.css   # Main page styles
│   │   ├── commerce.css # Commerce-specific styles
│   │   ├── industry.css # Industry-specific styles
│   │   └── service.css  # Service-specific styles
│   └── js/             # JavaScript files
│       ├── commerce.js # Commerce data visualization
│       ├── industry.js # Industry data visualization
│       └── service.js  # Service data visualization
└── db/                 # Database configuration
    ├── config.py       # Database configuration module
    ├── config.yaml     # Database connection settings
    └── db.py           # Database connection handlers
```

## Getting Started

To run the project:

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Configure databases:

    - Set up PostgreSQL and MongoDB
    - Update connection settings in `db/config.yaml`
    - Create necessary database users and permissions
    - Initialize database schemas

3. Start the application:

    ```bash
    python run.py
    ```

4. Access the web interface at `http://localhost:5000`

The system will automatically fetch initial data and begin periodic updates. The web interface provides access to various economic indicators and visualizations for the commerce, industry, and services sectors.

## Future Improvements

While Ecotrack implements a data pipeline from ingestion to visualization, several enhancements have been identified to extend its functionality, improve performance, and increase its scalability for production-level deployment. Future development goals include:

- **Enhanced Frontend Interactivity**: Integrate advanced JavaScript frameworks such as React.js or Vue.js to create a more dynamic and responsive user interface. This would allow real-time data updates, interactive filtering, and improved state management across complex visualizations.

- **User Authentication and Authorization**: Implement a secure authentication system to manage user access and data permissions. Future versions could support user accounts, personalized dashboards, and restricted administrative endpoints for managing datasets and schedules. Additionally, a collaborative functionality could be introduced, allowing authenticated users to contribute their own dashboards, upload new data sources, and share customized analyses with the broader community, thereby fostering a participatory and extensible data ecosystem within the platform.

- **Expanded Data Sources**: Broaden the range of economic indicators by integrating additional APIs and databases beyond IBGE's SIDRA, such as the Central Bank of Brazil (BACEN) or international economic datasets (e.g., World Bank, OECD). This would allow richer cross-sectoral and international comparative analyses.

- **Data Caching and Performance Optimization**: Introduce caching mechanisms such as Redis to reduce database load and improve response times for frequently accessed datasets. Optimize aggregation queries and API endpoints to handle higher traffic volumes and larger datasets.

- **Advanced Data Analytics and Machine Learning**: Extend the data processing pipeline to incorporate predictive analytics and machine learning models, enabling forecasting of economic trends and anomaly detection. These models could be trained using historical data aggregated through Ecotrack’s pipeline.

- **Scalable Deployment Architecture**: Containerize the application using Docker and orchestrate deployment with Kubernetes to enable horizontal scaling, fault tolerance, and easier cloud deployment. Future deployment strategies could involve continuous integration and continuous deployment (CI/CD) pipelines for streamlined updates.

- **Data Versioning and Auditing**: Implement robust data version control mechanisms to track changes across datasets and support historical auditing. This would allow users to view and analyze past states of economic indicators over time.

- **Internationalization (i18n)**: Support multi-language interfaces and localized data formats to make the platform accessible to a broader audience.

- **Comprehensive API Documentation**: Develop through API documentation using tools like Swagger or Redoc to provide clear usage guidelines for external developers and promote possible third-party integrations.

## Installation

(faltou o passo para configurar o postgres)

1. Clone the repository:

    ```bash
    git clone [REPOSITORY_URL]
    cd Ecotrack
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

4. Configure PostgreSQL:

    - Ensure PostgreSQL is installed and running
    - Create a new database
    - Create a new user and credentials
    - Grant necessary permissions to the user
    - Connection settings are located in `db/config.yaml`
    - You can modify the connection settings in `db/config.yaml` if needed

    Example PostgreSQL setup commands:

    ```sql
    
    CREATE DATABASE statistics;
    CREATE USER app_user WITH PASSWORD 'app_password';
    GRANT ALL PRIVILEGES ON DATABASE statistics TO app_user;
    ```

5. Configure MongoDB:

    - Ensure MongoDB is installed and running
    - Create a new database
    - Create a new user and credentials
    - Grant necessary permissions to the user
    - Connection settings are located in `db/config.yaml`
    - You can modify the connection settings in `db/config.yaml` if needed

    Example MongoDB setup commands:

    ```javascript

    use investment_analyzer
    db.createUser({
      user: "mongo_user",
      pwd: "mongo_password",
      roles: [{ role: "readWrite", db: "investment_analyzer" }]
    })
    ```

    Note: The MongoDB collections will be automatically created by the application when data is aggregated. The collections store processed data from PostgreSQL for visualization in the frontend.

## Usage

1. Start the application:

    ```bash
    python run.py
    ```

2. Access the web interface:

    - Open your browser and navigate to `http://localhost:5000`

## Main APIs

### Commerce

- `/api/commerce/volume/series` - Volume time series
- `/api/commerce/division` - Sector division
- `/api/commerce/ranking` - Performance ranking
- `/api/commerce/revenue-expense/series` - Revenue and expense series
- `/api/commerce/revenue-expense/grouped` - Revenue and expense grouped data

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
- Developed by [Gabrielly Monarca](https://github.com/gabriellymonarca) as a Harvard CS50x final project

## Additional Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SIDRA API Documentation](https://api.sidra.ibge.gov.br/)
