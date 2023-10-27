from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to create the temperatures table if it doesn't exist
def create_temperatures_table():
    conn = sqlite3.connect('temperatures.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,  -- Cambia 'INTEGER' a 'REAL' para permitir decimales
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert a temperature and created_at date into the database
def insert_temperature(temperature):
    conn = sqlite3.connect('temperatures.db')
    cursor = conn.cursor()
    current_time = datetime.now()
    cursor.execute('INSERT INTO temperatures (temperature, created_at) VALUES (?, ?)', (temperature, current_time))
    conn.commit()
    conn.close()

def is_valid_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

@app.route('/insert_temperature', methods=['POST'])
def insert_temperature_route():
    try:
        temperature = request.form.get('temperature')

        if temperature is None or not is_valid_float(temperature):
            return "Temperature must be a valid decimal number", 400

        create_temperatures_table()  # Crea la tabla si no existe
        insert_temperature(float(temperature))  # Inserta la temperatura en la base de datos

        return "Temperature recorded successfully", 201

    except Exception as e:
        return "Internal Server Error", 500

    
# Define una ruta para recuperar temperaturas por fecha
@app.route('/get_temperatures', methods=['GET'])
def get_temperatures():
    try:
        date_str = request.args.get('date')
        
        # Verifica si se proporciona la fecha
        if not date_str:
            return "La fecha no ha sido proporcionada", 400
        
        # Convierte la fecha proporcionada a un objeto datetime
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Conecta a la base de datos
        conn = sqlite3.connect('temperatures.db')
        cursor = conn.cursor()
        
        # Consulta las temperaturas para la fecha proporcionada
        cursor.execute("SELECT temperature, created_at FROM temperatures WHERE DATE(created_at) = ?", (date.date(),))
        result = cursor.fetchall()
        
        conn.close()
        
        if result:
            # Formatea los resultados como un JSON
            temperatures = [{'temperature': row[0], 'created_at': row[1]} for row in result]
            return jsonify(temperatures)
        else:
            return "No se encontraron registros para la fecha especificada", 404
    
    except Exception as e:
        return "Error interno del servidor", 500
    
@app.route('/get_last_5_minutes_temperatures', methods=['GET'])
def get_last_5_minutes_temperatures():
    try:
        # Obtén la fecha y hora actual
        current_time = datetime.now()

        # Calcula la fecha y hora de hace 5 minutos
        five_minutes_ago = current_time - timedelta(minutes=5)

        # Conecta a la base de datos
        conn = sqlite3.connect('temperatures.db')
        cursor = conn.cursor()

        # Consulta las temperaturas registradas en los últimos 5 minutos
        cursor.execute("SELECT temperature, created_at FROM temperatures WHERE created_at >= ?", (five_minutes_ago,))
        result = cursor.fetchall()

        conn.close()

        if result:
            # Formatea los resultados como un JSON
            temperatures = [{'temperature': row[0], 'created_at': row[1]} for row in result]
            return jsonify(temperatures)
        else:
            return "No se encontraron registros en los últimos 5 minutos", 404

    except Exception as e:
        return "Error interno del servidor", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

