from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

datos_recibidos = []
MAX_REGISTROS = 20

@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    temperatura = data.get('temperatura')
    humedad = data.get('humedad')
    humedad_suelo = data.get('humedad_suelo')

    datos_recibidos.append({
        'temperatura': temperatura,
        'humedad': humedad,
        'humedad_suelo': humedad_suelo,
        'timestamp': int(time.time() * 1000)
    })
    if len(datos_recibidos) > MAX_REGISTROS:
        datos_recibidos.pop(0)

    return jsonify({'mensaje': 'Datos recibidos correctamente'}), 200

@app.route('/ver-datos')
def ver_datos():
    html = """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>EcoMonitor - Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f8f9fa; }
            .sensor-card { padding: 1rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 1rem; }
            .value-display { font-size: 2rem; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h1 class="text-center mb-4"><i class="fas fa-seedling me-2"></i>EcoMonitor</h1>

            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="sensor-card text-center border-info">
                        <h5>Humedad Suelo</h5>
                        <div class="value-display text-info">{{ datos[-1].humedad_suelo if datos else '--' }}%</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="sensor-card text-center border-danger">
                        <h5>Temperatura</h5>
                        <div class="value-display text-danger">{{ datos[-1].temperatura if datos else '--' }}°C</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="sensor-card text-center border-primary">
                        <h5>Humedad Relativa</h5>
                        <div class="value-display text-primary">{{ datos[-1].humedad if datos else '--' }}%</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4"><div id="humedadChart"></div></div>
                <div class="col-md-4"><div id="temperaturaChart"></div></div>
                <div class="col-md-4"><div id="sueloChart"></div></div>
            </div>
        </div>

        <script>
            const datos = {{ datos | tojson }};
            const timestamps = datos.map(d => d.timestamp);
            const humedad = datos.map(d => parseFloat(d.humedad));
            const temperatura = datos.map(d => parseFloat(d.temperatura));
            const humedadSuelo = datos.map(d => parseFloat(d.humedad_suelo));

            const generarGrafico = (id, data, nombre, color) => {
                Highcharts.chart(id, {
                    chart: { type: 'spline', backgroundColor: 'transparent' },
                    title: { text: nombre },
                    xAxis: {
                        type: 'datetime',
                        categories: timestamps,
                        labels: {
                            formatter: function() {
                                return new Date(this.value).toLocaleTimeString();
                            }
                        }
                    },
                    yAxis: { title: { text: null } },
                    series: [{ name: nombre, data: data }],
                    credits: { enabled: false },
                    colors: [color]
                });
            };

            generarGrafico('humedadChart', humedad, 'Humedad Relativa', '#3498db');
            generarGrafico('temperaturaChart', temperatura, 'Temperatura', '#e74c3c');
            generarGrafico('sueloChart', humedadSuelo, 'Humedad Suelo', '#27ae60');
        </script>
    </body>
    </html>"""
    return render_template_string(html, datos=datos_recibidos)

if __name__ == '__main__':
    app.run(debug=True, port=10000)

