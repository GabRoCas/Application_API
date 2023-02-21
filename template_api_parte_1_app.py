from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
import sklearn
import pickle
import numpy as np

app = Flask(__name__)
app.config['DEBUG'] = True

# Ruta a la carpeta donde esté el modelo guardado
root = '/home/gabsrodcas/modelo_clase/' # .. -> (tengo que poner el del directorio del pythonanywhere)
root_db = "/home/gabsrodcas/databases/"
model = pickle.load(open(root + 'advertising.model', 'rb'))

# POST {"TV":, "radio":, "newspaper":} -> It returns the sales prediction for input investments
@app.route('/predict', methods=['POST'])
def get_predict():

    # Get current time for the PREDICTIONS table
    str_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Establish SQLITE3 connection and create a cursor to operate upon the DB
    conn = sqlite3.connect(root + "advertising.db")
    crs = conn.cursor()
    

    # Get POST JSON data
    data = request.get_json()
    tv = data.get("TV",0)
    radio = data.get("radio",0)
    newspaper = data.get("newspaper",0)

    # Model prediciton
    X = [[tv,radio,newspaper]]
    pred = model.predict(np.array([[tv,radio,newspaper]]))[0]

    # Save prediction in PREDICTIONS table
    crs.execute(''' INSERT INTO PREDICTIONS(pred_date,TV,radio,newspaper,predictions)
                VALUES (?,?,?,?,?) ''', (str_time,tv,radio,newspaper,pred))
    conn.commit()
    conn.close()
    return str(pred), 200 # Return the prediction

@app.route('/review_predicts', methods=["GET"])
def return_predicts():
    conn=sqlite3.connect(root_db + "advertising.db")
    crs = conn.cursor()
    query = "SELECT * FROM PREDICTIONS"
    resultado = jsonify(crs.execute(query).fetchall())
    conn.close()

    return resultado

@app.route('/', methods=['GET'])
def home():
	return "<h1>Hola, ¡soy tu predictor de ventas!</h1></p> Pregúntame lo que necesites, ¡estoy listo!.</p>"
    

#app.run(port=4000) lo llama otro programa