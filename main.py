from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Lista para guardar los datos de los últimos 10 registros
datos_recibidos = []  
MAX_REGISTROS = 10  # Número máximo de registros a mantener

# Ruta para recibir los datos desde la Raspberry Pi
@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    temperatura = data.get('temperatura')
    humedad = data.get('humedad')
    humedad_suelo = data.get('humedad_suelo')

    # Añadir los datos a la lista y asegurarse de que no haya más de MAX_REGISTROS elementos
    datos_recibidos.append({
        'temperatura': temperatura,
        'humedad': humedad,
        'humedad_suelo': humedad_suelo
    })
    if len(datos_recibidos) > MAX_REGISTROS:
        datos_recibidos.pop(0)  # Eliminar el primer elemento si excede el límite

    print(f"Temperatura: {temperatura}, Humedad: {humedad}, Humedad Suelo: {humedad_suelo}")
    return jsonify({'mensaje': 'Datos recibidos correctamente'}), 200

# Ruta para mostrar los datos en una página web
@app.route('/ver-datos')
def ver_datos():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datos de la Planta</title>
        <style>
            table { border-collapse: collapse; width: 60%; margin: auto; }
            th, td { border: 1px solid #999; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            h1 { text-align: center; }
        </style>
    </head>
    <body>
        <h1>Últimos Datos Recibidos</h1>
        <table>
            <tr>
                <th>Temperatura (°C)</th>
                <th>Humedad (%)</th>
                <th>Humedad Suelo (%)</th>
            </tr>
            {% for d in datos %}
            <tr>
                <td>{{ d.temperatura }}</td>
                <td>{{ d.humedad }}</td>
                <td>{{ d.humedad_suelo }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, datos=datos_recibidos)

# Ejecutar localmente (esto lo puedes omitir en Render)
if __name__ == '__main__':
    app.run(debug=True, port=10000)
