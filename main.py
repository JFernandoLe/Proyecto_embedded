from flask import Flask, request, jsonify
import os

app = Flask(__name__)

datos_planta = {}

@app.route('/datos', methods=['POST'])
def recibir_datos():
    global datos_planta
    datos_planta = request.json
    print("Datos recibidos:", datos_planta)
    return jsonify({"status": "ok"})

@app.route('/datos', methods=['GET'])
def enviar_datos():
    return jsonify(datos_planta)

# Configura el puerto dinámico
port = int(os.environ.get("PORT", 10000))  # Usado en Render para configurar el puerto
app.run(host='0.0.0.0', port=port)
