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

@app.route('/api/ultimos-datos')
def ultimos_datos():
    return jsonify(datos_recibidos)

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
                <div class="col-md-4"><div id="sueloChart"></div></div>
                <div class="col-md-4"><div id="temperaturaChart"></div></div>
                <div class="col-md-4"><div id="humedadChart"></div></div>
            </div>
        </div>

        <script>
    let chartHumedad, chartTemperatura, chartSuelo;

    function inicializarGraficos() {
        
        
        chartHumedad = Highcharts.chart('humedadChart', {
            chart: { type: 'spline', backgroundColor: 'transparent' },
            title: { text: 'Humedad Relativa' },
            xAxis: { type: 'datetime', labels: { format: '{value:%H:%M:%S}' } },
            yAxis: { title: { text: null } },
            series: [{ name: 'Humedad', data: [] }],
            credits: { enabled: false },
            colors: ['#3498db']
        });

        chartTemperatura = Highcharts.chart('temperaturaChart', {
            chart: { type: 'spline', backgroundColor: 'transparent' },
            title: { text: 'Temperatura' },
            xAxis: { type: 'datetime', labels: { format: '{value:%H:%M:%S}' } },
            yAxis: { title: { text: null } },
            series: [{ name: 'Temperatura', data: [] }],
            credits: { enabled: false },
            colors: ['#e74c3c']
        });

        chartSuelo = Highcharts.chart('sueloChart', {
            chart: { type: 'spline', backgroundColor: 'transparent' },
            title: { text: 'Humedad del Suelo' },
            xAxis: { type: 'datetime', labels: { format: '{value:%H:%M:%S}' } },
            yAxis: { title: { text: null } },
            series: [{ name: 'H. Suelo', data: [] }],
            credits: { enabled: false },
            colors: ['#27ae60']
        });
    }

    function actualizarDatos() {
        fetch('/api/ultimos-datos')
            .then(res => res.json())
            .then(datos => {
                if (datos.length === 0) return;

                const ult = datos[datos.length - 1];
                document.querySelector('.text-info').innerText = `${ult.humedad_suelo}%`;
                document.querySelector('.text-danger').innerText = `${ult.temperatura}°C`;
                document.querySelector('.text-primary').innerText = `${ult.humedad}%`;

                const hum = datos.map(d => [d.timestamp, parseFloat(d.humedad)]);
                const temp = datos.map(d => [d.timestamp, parseFloat(d.temperatura)]);
                const suelo = datos.map(d => [d.timestamp, parseFloat(d.humedad_suelo)]);

                chartHumedad.series[0].setData(hum);
                chartTemperatura.series[0].setData(temp);
                chartSuelo.series[0].setData(suelo);
            });
    }

    inicializarGraficos();
    actualizarDatos();
    setInterval(actualizarDatos, 5000); // actualiza cada 5 segundos
    </script>

    </body>
    </html>"""
    return render_template_string(html, datos=datos_recibidos)

if __name__ == '__main__':
    app.run(debug=True, port=10000)

