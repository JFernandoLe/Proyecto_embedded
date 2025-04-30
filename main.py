from flask import Flask, request, jsonify

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Asegúrate de escuchar en todas las interfaces y el puerto adecuado
