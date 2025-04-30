from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    temperatura = data.get('temperatura')
    humedad = data.get('humedad')
    luz = data.get('luz')
    print(f"Temperatura: {temperatura}, Humedad: {humedad}, Luz: {luz}")
    return jsonify({'mensaje': 'Datos recibidos correctamente'}), 200
