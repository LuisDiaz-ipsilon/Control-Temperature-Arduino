import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, jsonify
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)

# Función para obtener los datos de temperatura
def get_temperature_data():
    response = requests.get("http://localhost:5000/get_last_5_minutes_temperatures")

    if response.status_code == 200:
        data = response.json()
        temperatures = [entry['temperature'] for entry in data]
        timestamps = [datetime.strptime(entry['created_at'], "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S") for entry in data]

        return timestamps, temperatures
    else:
        return [], []

#Renderizar la pagina
@app.route('/')
def index():
    return render_template('index.html')

#Retornar JSON con los datos necesarios para la grafica
@app.route('/get_chart_data')
def get_chart_data():
    timestamps, temperatures = get_temperature_data()

    # Crear una gráfica Plotly
    data = {
        'x': timestamps,
        'y': temperatures,
        'type': 'scatter',
        'mode': 'lines+markers',
        'marker': {'color': 'blue'},
    }

    layout = {
        'xaxis': {
            'title': 'Tiempo (hh:mm:ss)',
        },
        'yaxis': {
            'title': 'Temperatura (°C)',
        },
        'autosize': False,
        'width': 800,
        'height': 400,
    }

    # Generar el objeto figura Plotly
    figure = {
        'data': [data],
        'layout': layout,
    }

    # Devolver la configuración de la gráfica como JSON
    return jsonify(figure)


#Obtener el ultimo dato de temperatura
@app.route('/get_last_temperature')
def get_last_temperature():
    # Llama a la función para obtener los datos de temperatura
    timestamps, temperatures = get_temperature_data()

    # Verifica si hay datos de temperatura
    if timestamps and temperatures:
        # Obtiene la temperatura más reciente
        last_temperature = temperatures[-1]

        # Devuelve la última temperatura como JSON
        return jsonify({'temperature': last_temperature})
    else:
        # Si no hay datos de temperatura, devuelve un mensaje de error
        return jsonify({'error': 'No se encontraron datos de temperatura'}),
    
@app.route('/get_temperature_by_date/<date>', methods=['GET'])
def get_temperature_by_date(date):
    # Llama al backend para obtener los datos de temperatura para la fecha especificada
    response = requests.get(f"http://192.168.137.1:5000/get_temperatures?date={date}")
    
    
    if response.status_code == 200:
        
        data = response.json()
        
        # Crea una gráfica con los datos de temperatura
        timestamps = [entry['created_at'] for entry in data]
        temperatures = [entry['temperature'] for entry in data]

        # Convertir las marcas de tiempo a objetos datetime
        timestamps = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f") for ts in timestamps]

        # Crear un diccionario para almacenar los totales de temperatura y recuentos por hora
        hourly_data = {}
        for ts, temp in zip(timestamps, temperatures):
            hour = ts.hour
            if hour not in hourly_data:
                hourly_data[hour] = {'total_temperature': temp, 'count': 1}
            else:
                hourly_data[hour]['total_temperature'] += temp
                hourly_data[hour]['count'] += 1

        # Calcular los promedios por hora
        hourly_averages = []
        for hour, data in hourly_data.items():
            average_temperature = data['total_temperature'] / data['count']
            hourly_averages.append((hour, average_temperature))

        # Desempaquetar los datos en horas y temperaturas promedio
        hours, average_temperatures = zip(*hourly_averages)

        # Configurar la gráfica
        plt.plot(hours, average_temperatures)
        plt.xlabel('Hora del día')
        plt.ylabel('Temperatura promedio (°C)')
        plt.xticks(range(24))  # Etiquetas del eje X de 0 a 23 (horas)

        # Guardar la gráfica como imagen
        image_filename = f'temperature_{date}.png'
        plt.savefig(image_filename)
        plt.close()
        return data;
    else:
        return jsonify({'error': 'No se pudieron recuperar los datos de temperatura'})
    
    

        
    return data



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
