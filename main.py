from flask import Flask, request, jsonify, render_template_string


app = Flask(__name__)

# Lista para guardar los datos de los últimos 10 registros
datos_recibidos = []  
MAX_REGISTROS = 10  # Número máximo de registros a mantener

# Ruta para recibir los datos desde la Raspberry Pi
from datetime import datetime

@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    temperatura = data.get('temperatura')
    humedad = data.get('humedad')
    luz = data.get('luz')

    # Añadir un timestamp
    timestamp = int(datetime.utcnow().timestamp() * 1000)  # Obtener el tiempo en milisegundos

    # Añadir los datos a la lista
    datos_recibidos.append({
        'temperatura': temperatura,
        'humedad': humedad,
        'luz': luz,
        'timestamp': timestamp
    })

    # Limitar la lista a los últimos 10 registros
    if len(datos_recibidos) > MAX_REGISTROS:
        datos_recibidos.pop(0)

    print(f"Temperatura: {temperatura}, Humedad: {humedad}, Luz: {luz}, Timestamp: {timestamp}")
    return jsonify({'mensaje': 'Datos recibidos correctamente'}), 200


# Ruta para mostrar los datos
@app.route('/ver-datos')
def ver_datos():
    html = """
    <!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoMonitor - Dashboard Agrícola</title>
    
    <!-- Dependencias -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://kit.fontawesome.com/9d05a3393b.js" crossorigin="anonymous"></script>
    
    <style>
        /* Estilos personalizados (sin cambios) */
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f1c40f;
            --danger-color: #e74c3c;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
        }

        .dashboard-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, #34495e 100%);
            color: white;
            padding: 2rem;
            border-radius: 0 0 25px 25px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }

        .sensor-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            border-left: 4px solid;
        }

        .sensor-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        .sensor-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }

        .value-display {
            font-size: 2.8rem;
            font-weight: 600;
            margin: 0.5rem 0;
            letter-spacing: -1px;
        }

        .unit {
            font-size: 1.1rem;
            color: #6c757d;
            font-weight: 400;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 0.5rem;
            vertical-align: middle;
        }

        .data-age {
            font-size: 0.9rem;
            color: #95a5a6;
            margin-top: 0.5rem;
        }
    </style>

</head>
<body>
    <header class="dashboard-header text-center">
        <h1 class="mb-3">
            <i class="fas fa-seedling me-2"></i>EcoMonitor
            <span class="status-indicator bg-success" title="Conectado"></span>
        </h1>
        <p class="mb-0 text-muted">Monitoreo en tiempo real de parámetros agrícolas</p>
    </header>

    <div class="container-lg">
        <!-- Tarjetas de valores actuales -->
        <div class="row g-4 mb-4">
            <!-- Humedad -->
            <div class="col-md-4">
                <div class="sensor-card border-info">
                    <div class="text-center">
                        <i class="fas fa-tint sensor-icon text-info"></i>
                        <h3>Humedad del Suelo</h3>
                        <div class="value-display">
                            <span id="currentHumidity">--</span><span class="unit">%</span>
                        </div>
                        <div class="data-age" id="humedadTime">hace -- seg</div>
                    </div>
                </div>
            </div>

            <!-- Temperatura -->
            <div class="col-md-4">
                <div class="sensor-card border-danger">
                    <div class="text-center">
                        <i class="fas fa-thermometer-half sensor-icon text-danger"></i>
                        <h3>Temperatura</h3>
                        <div class="value-display">
                            <span id="currentTemperature">--</span><span class="unit">°C</span>
                        </div>
                        <div class="data-age" id="temperaturaTime">hace -- seg</div>
                    </div>
                </div>
            </div>

            <!-- Iluminación -->
            <div class="col-md-4">
                <div class="sensor-card border-warning">
                    <div class="text-center">
                        <i class="fas fa-sun sensor-icon text-warning"></i>
                        <h3>Iluminación</h3>
                        <div class="value-display">
                            <span id="currentIllumination">--</span><span class="unit">lux</span>
                        </div>
                        <div class="data-age" id="iluminacionTime">hace -- seg</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos -->
        <div class="row g-4">
            <div class="col-md-4">
                <div class="chart-container">
                    <div id="humedadChart"></div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="chart-container">
                    <div id="temperaturaChart"></div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="chart-container">
                    <div id="iluminacionChart"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Función para obtener los datos desde la API
        const fetchData = async () => {
    try {
        const response = await fetch('https://proyecto-embedded.onrender.com/api/datos', {
            method: 'POST',  // Cambiar de GET a POST
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})  // Asegúrate de enviar un cuerpo vacío o los datos que corresponda
        });
        const data = await response.json();
        updateDisplay(data);
    } catch (error) {
        console.error('Error al obtener datos de la API:', error);
    }
};


        // Función para actualizar la página con los datos recibidos
        const updateDisplay = (data) => {
            const timeAgo = Math.floor((Date.now() - data.timestamp) / 1000);
            
            // Actualizar valores
            document.getElementById('currentHumidity').textContent = data.humedad.toFixed(1);
            document.getElementById('currentTemperature').textContent = data.temperatura.toFixed(1);
            document.getElementById('currentIllumination').textContent = Math.floor(data.iluminacion);
            
            // Actualizar tiempos
            document.querySelectorAll('.data-age').forEach(el => {
                el.textContent = `hace ${timeAgo} seg`;
            });

            // Actualizar gráficos
            updateCharts(data);
        };

        // Función para actualizar los gráficos
        const updateCharts = (data) => {
            charts.humedad.series[0].addPoint([data.timestamp, data.humedad], true, false);
            charts.temperatura.series[0].addPoint([data.timestamp, data.temperatura], true, false);
            charts.iluminacion.series[0].addPoint([data.timestamp, data.iluminacion], true, false);
        };

        // Llamar a la API cada 5 segundos
        setInterval(fetchData, 5000);

        // Inicialización de gráficos
        const initChart = (container, title, color) => {
            return Highcharts.chart(container, {
                chart: { type: 'spline', backgroundColor: 'transparent', height: 300 },
                title: { text: null },
                colors: [color],
                yAxis: { title: { text: null }, gridLineColor: '#f0f0f0' },
                xAxis: { type: 'datetime', labels: { format: '{value:%H:%M}' } },
                legend: { enabled: false },
                series: [{ name: title, data: [], lineWidth: 2, marker: { enabled: false } }],
                plotOptions: { series: { animation: { duration: 1000 } } }
            });
        };

        // Crear los gráficos
        const charts = {
            humedad: initChart('humedadChart', 'Humedad', '#3498db'),
            temperatura: initChart('temperaturaChart', 'Temperatura', '#e74c3c'),
            iluminacion: initChart('iluminacionChart', 'Iluminación', '#f1c40f')
        };

        // Obtener datos al cargar la página
        fetchData();
    </script>
</body>
</html>

    """
    return render_template_string(html, datos=datos_recibidos)

# Ejecutar localmente (esto lo puedes omitir en Render)
if __name__ == '__main__':
    app.run(debug=True, port=10000)
