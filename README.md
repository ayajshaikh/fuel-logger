# fuel-logger: a Petrol Records Management Web Application
Simple Application to log the Fuel of a Vehicle

This project is a Flask web application for managing petrol records. It supports CRUD operations for vehicles, stations, and fuel records, and provides analytics visualisations.

## Features

- **Vehicle Management**: Add, edit, and view vehicles.
- **Station Management**: Add, edit, and view petrol stations.
- **Fuel Record Management**: Add, edit, view, and delete fuel fill-up records.
- **Analytics Visualisation**: Generate and display analytics for fuel consumption and costs.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ayajshaikh/fuel-logger.git
   cd fuel-logger
   ```
2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```

## Installation
1. Open your browser and go to http://localhost:5000
2. Use the interface to manage vehicles, stations, and fuel records.
3. Navigate to /analytics to view fuel consumption and cost trends.
