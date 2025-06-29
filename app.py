"""
app.py

This module implements a Flask web application for managing petrol records.
It supports CRUD operations for vehicles, stations, and fuel records, and
provides analytics visualisations.

Modules:
    - io
    - base64
    - sqlite3
    - matplotlib.pyplot
    - collections.defaultdict
    - datetime
    - flask

Functions:
    - init_db()
    - index()
    - add_record()
    - view_records()
    - edit_record(id)
    - delete_record(id)
    - view_stations()
    - show_add_station_form()
    - handle_add_station()
    - edit_station(id)
    - view_vehicle()
    - show_add_vehicle_form()
    - add_vehicle()
    - edit_vehicle(id)
    - get_fuels(vehicle_id)
    - analytics()
"""

from flask import Flask, render_template, request, redirect
import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
import datetime
import io
import base64

app = Flask(__name__)

def init_db():
    """
    Initialises the SQLite database and creates necessary tables if they do not exist.
    Tables:
        - ref_fuel: Reference table for fuel types.
        - stations: Stores petrol station information.
        - vehicle: Stores vehicle details.
        - records: Stores fuel fill-up records.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    # Create ref_fuel table
    c.execute('''CREATE TABLE IF NOT EXISTS ref_fuel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    fuel_type TEXT,
                    type TEXT
                )''')
    # Create stations table
    c.execute('''CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    address TEXT,
                    location TEXT
                )''')
    # Create vehicle table
    c.execute('''CREATE TABLE IF NOT EXISTS vehicle (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    make TEXT,
                    model TEXT,
                    registration TEXT,
                    fuel TEXT
                )''')
    # Create records table
    c.execute('''CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    liters REAL,
                    cost REAL,
                    odometer REAL,
                    rate REAL,
                    station_id INTEGER,
                    vehicle_id INTEGER,
                    fuel_type_id INTEGER,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
                    FOREIGN KEY (station_id) REFERENCES stations(id)
                    FOREIGN KEY (fuel_type_id) REFERENCES ref_fuel(id)
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """
    Renders the home page with links to lists of all records, stations and vehicles.
    
    Returns:
        str: Rendered HTML template for the index page.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('SELECT * FROM records')
    records = c.fetchall()
    c.execute('SELECT * FROM stations')
    stations = c.fetchall()
    c.execute('SELECT * FROM vehicle')
    vehicles = c.fetchall()
    c.execute('SELECT * FROM ref_fuel')
    fuels = c.fetchall()
    conn.close()
    return render_template('index.html', records=records, stations=stations, vehicles=vehicles, fuels=fuels)

@app.route('/record/add', methods=['POST'])
def add_record():
    """
    Adds a new fuel record to the database.

    Retrieves form data from the request, calculates the rate (cost per liter),
    and inserts a new record into the `records` table.

    Returns:
        Response: Redirects to the home page or returns an error message.
    """
    try:
        date = request.form['date']
        liters = float(request.form['liters'])
        cost = float(request.form['cost'])
        odometer = ''
        if(request.form['odometer'] != ''):
            odometer = float(request.form['odometer'])
        station_id = int(request.form['station_id'])
        vehicle_id = int(request.form['vehicle_id'])
        fuel_type_id = int(request.form['fuel_type_id'])
        rate = cost / liters if liters != 0 else 0.0

        conn = sqlite3.connect('petrol_records.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO records (date, liters, cost, odometer, rate, station_id, vehicle_id, fuel_type_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, liters, cost, odometer, rate, station_id, vehicle_id, fuel_type_id))
        conn.commit()
        conn.close()
        return redirect('/')
    except Exception as e:
        return f"Error: {e}"

@app.route('/records')
def view_records():
    """
    Displays all fuel records.

    Returns:
        str: Rendered HTML template showing all records.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('''
        SELECT records.id, records.date, ref_fuel.name, records.liters, records.cost,
               records.odometer, records.rate, stations.name, vehicle.registration
        FROM records
        JOIN vehicle ON records.vehicle_id = vehicle.id
        JOIN ref_fuel ON records.fuel_type_id = ref_fuel.id
        JOIN stations ON records.station_id = stations.id
    ''')
    records = c.fetchall()
    conn.close()
    return render_template('records.html', records=records)

@app.route('/record/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    """
    Edits an existing fuel record.

    Args:
        id (int): The ID of the record to edit.

    Returns:
        str: Rendered HTML form for editing or redirects after update.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()

    if request.method == 'POST':
        date = request.form['date']
        liters = float(request.form['liters'])
        cost = float(request.form['cost'])
        odometer = float(request.form['odometer'])
        station_id = int(request.form['station_id'])
        vehicle_id = int(request.form['vehicle_id'])
        fuel_type_id = int(request.form['fuel_type_id'])
        rate = cost / liters if liters != 0 else 0.0

        c.execute('''
            UPDATE records
            SET date = ?, liters = ?, cost = ?, odometer = ?, rate = ?, station_id = ?, vehicle_id = ?, fuel_type_id = ?
            WHERE id = ?
        ''', (date, liters, cost, odometer, rate, station_id, vehicle_id, fuel_type_id, id))
        conn.commit()
        conn.close()
        return redirect('/records')
    else:
        c.execute('SELECT * FROM records WHERE id = ?', (id,))
        record = c.fetchone()
        c.execute('SELECT * FROM stations')
        stations = c.fetchall()
        c.execute('SELECT * FROM vehicle')
        vehicles = c.fetchall()
        c.execute('''
            SELECT ref_fuel.id, ref_fuel.name, ref_fuel.fuel_type, ref_fuel.type
            FROM ref_fuel
            JOIN vehicle ON vehicle.fuel = ref_fuel.fuel_type
            JOIN records ON records.id = ?
        ''', (id,))
        fuels = c.fetchall()
        conn.close()
        return render_template('edit.html', record=record, stations=stations, vehicles=vehicles, fuels=fuels)

@app.route('/record/delete/<int:id>', methods=['POST'])
def delete_record(id):
    """
    Deletes a fuel record from the database.

    Args:
        id (int): The ID of the record to delete.

    Returns:
        Response: Redirects to the records page after deletion.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('DELETE FROM records WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/records')

# ------------------- Station Routes -------------------

@app.route('/station')
def view_stations():
    """
    Displays a list of all petrol stations.

    Returns:
        str: Rendered HTML template showing all stations.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('SELECT id, name, address, location FROM stations')
    stations = c.fetchall()
    conn.close()
    return render_template('/station/list.html', stations=stations)

@app.route('/station/add', methods=['GET'])
def show_add_station_form():
    """
    Displays the form to add a new petrol station.

    Returns:
        str: Rendered HTML form for adding a station.
    """
    return render_template('/station/add.html')

@app.route('/station/add', methods=['POST'])
def handle_add_station():
    """
    Handles submission of the add station form.

    Inserts a new station into the database.

    Returns:
        Response: Redirects to the home page after insertion.
    """
    name = request.form['name']
    address = request.form['address']
    location = request.form['location']

    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('INSERT INTO stations (name, address, location) VALUES (?, ?, ?)',
              (name, address, location))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/station/edit/<int:id>', methods=['GET', 'POST'])
def edit_station(id):
    """
    Edits an existing petrol station.

    Args:
        id (int): The ID of the station to edit.

    Returns:
        str: Rendered HTML form for editing or redirects after update.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        location = request.form['location']
        c.execute('UPDATE stations SET name = ?, address = ?, location = ? WHERE id = ?',
                  (name, address, location, id))
        conn.commit()
        conn.close()
        return redirect('/station')
    else:
        c.execute('SELECT * FROM stations WHERE id = ?', (id,))
        record = c.fetchone()
        conn.close()
        return render_template('/station/edit.html', record=record)

# ------------------- Vehicle Routes -------------------

@app.route('/vehicle')
def view_vehicle():
    """
    Displays a list of all vehicles.

    Returns:
        str: Rendered HTML template showing all vehicles.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('SELECT id, make, model, registration, fuel FROM vehicle')
    vehicles = c.fetchall()
    conn.close()
    return render_template('/vehicle/list.html', vehicles=vehicles)

@app.route('/vehicle/add', methods=['GET'])
def show_add_vehicle_form():
    """
    Displays the form to add a new vehicle.

    Fetches available fuel types from the database.

    Returns:
        str: Rendered HTML form for adding a vehicle.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT fuel_type FROM ref_fuel')
    fuels = c.fetchall()
    conn.close()
    return render_template('/vehicle/add.html', fuels=fuels)

@app.route('/vehicle/add', methods=['POST'])
def add_vehicle():
    """
    Handles submission of the add vehicle form.

    Inserts a new vehicle into the database.

    Returns:
        Response: Redirects to the vehicle list page after insertion.
    """
    make = request.form['make']
    model = request.form['model']
    fuel = request.form['fuelType']
    registration = request.form['registration']

    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('INSERT INTO vehicle (make, model, registration, fuel) VALUES (?, ?, ?, ?)',
              (make, model, registration, fuel))
    conn.commit()
    conn.close()
    return redirect('/vehicle')

@app.route('/vehicle/edit/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    """
    Edits an existing vehicle.

    Args:
        id (int): The ID of the vehicle to edit.

    Returns:
        str: Rendered HTML form for editing or redirects after update.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()

    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        fuel = request.form['fuel_type_id']
        registration = request.form['registration']
        c.execute('UPDATE vehicle SET make = ?, model = ?, registration = ?, fuel = ? WHERE id = ?',
                  (make, model, registration, fuel, id))
        conn.commit()
        conn.close()
        return redirect('/vehicle')
    else:
        c.execute('SELECT id, make, model, registration, fuel FROM vehicle WHERE id = ?', (id,))
        record = c.fetchone()
        c.execute('SELECT DISTINCT fuel_type FROM ref_fuel')
        fuels = c.fetchall()
        conn.close()
        return render_template('/vehicle/edit.html', record=record, fuels=fuels)

@app.route('/vehicle/fuel/type/get/<int:vehicle_id>')
def get_fuels(vehicle_id):
    """
    Retrieves fuel types compatible with a specific vehicle.

    Args:
        vehicle_id (int): The ID of the vehicle.

    Returns:
        dict: A dictionary containing a list of compatible fuel types.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('SELECT fuel FROM vehicle WHERE id = ?', (vehicle_id,))
    vehicle_fuel = c.fetchone()

    if vehicle_fuel:
        c.execute('SELECT id, name FROM ref_fuel WHERE fuel_type = ?', (vehicle_fuel[0],))
        fuels = c.fetchall()
    else:
        fuels = []

    conn.close()
    return {'fuels': fuels}

@app.route('/analytics')
def analytics():
    """
    Generates and displays analytics for fuel consumption and costs.

    This route fetches all fuel records, calculates monthly totals, average costs,
    and rates, and generates plots using matplotlib. The plots are embedded in the
    rendered HTML as a base64-encoded image.

    Returns:
        str: Rendered HTML template with embedded analytics graph.
    """
    conn = sqlite3.connect('petrol_records.db')
    c = conn.cursor()
    c.execute('''
        SELECT records.date, records.liters, records.cost, records.odometer, records.rate,
               stations.name, vehicle.registration
        FROM records
        JOIN vehicle ON records.vehicle_id = vehicle.id
        JOIN stations ON records.station_id = stations.id
        ORDER BY records.date ASC
    ''')
    data = c.fetchall()
    conn.close()

    # Prepare and sort data
    dates = [row[0] for row in data]
    liters = [row[1] for row in data]
    costs = [row[2] for row in data]
    odometer = [row[3] for row in data]
    rates = [row[4] for row in data]
    name = [row[5] for row in data]
    registration = [row[6] for row in data]

    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))

    # Calculate averages
    avg_cost = sum(costs) / len(costs) if costs else 0
    avg_rate = sum(rates) / len(rates) if rates else 0

    # Calculate monthly costs
    monthly_costs = defaultdict(float)
    for date, cost in zip(dates, costs):
        month = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
        monthly_costs[month] += cost

    months = sorted(monthly_costs.keys())
    total_costs_per_month = [monthly_costs[month] for month in months]
    avg_monthly_cost = sum(total_costs_per_month) / len(total_costs_per_month) if total_costs_per_month else 0

    # Plot monthly costs
    axs[0].plot(months, total_costs_per_month, marker='s', color='green')
    axs[0].axhline(avg_monthly_cost, color='red', linestyle='--', label=f'Avg Monthly Cost: {avg_monthly_cost:.2f}')
    axs[0].set_title('Total Fuel Cost Per Month')
    axs[0].set_xlabel('Month')
    axs[0].tick_params(axis='x', rotation=90)
    axs[0].legend()

    # Plot cost per fill
    axs[1].plot(dates, costs, marker='o')
    axs[1].axhline(avg_cost, color='red', linestyle='--', label=f'Avg Cost: {avg_cost:.2f}')
    axs[1].set_title('Total Cost Per Fill')
    axs[1].set_xlabel('Date')
    axs[1].tick_params(axis='x', rotation=90)
    axs[1].legend()

    # Plot rate
    axs[2].plot(dates, rates, marker='x', color='orange')
    axs[2].axhline(avg_rate, color='red', linestyle='--', label=f'Avg Rate: {avg_rate:.2f}')
    axs[2].set_title('Rate')
    axs[2].set_xlabel('Date')
    axs[2].tick_params(axis='x', rotation=90)
    axs[2].legend()

    for ax in axs:
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.grid(True)

    # Convert plot to base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('analytics.html', graph=graph)
