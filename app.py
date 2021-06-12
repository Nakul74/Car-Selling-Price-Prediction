from flask import Flask
from pywebio.input import input,TEXT,radio,select,FLOAT,NUMBER
from pywebio.output import put_text
from pywebio.platform.flask import webio_view
import pandas as pd
import re
import argparse
from pywebio import start_server

from joblib import load
encoder = load('encoder.joblib')
scaler = load('scaler.joblib')
etree = load('etree.joblib')
seat_no = [2,4,5,6,7,8,9,10,14]

app = Flask(__name__)


def predict_price():
    data = pd.DataFrame()
    name = input("Enter the name of the Car： (eg. Renault KWID RXT)", type = TEXT)
    name = name.split(' ')[0]
    data['name'] = [name]
    
    def validate_date(d):
        if d>2021 and d<1990:
            return 'Enter valid year'
    
    year  = input("Enter the Year of purchase of the Car： (eg. 2013)", type = NUMBER, validate = validate_date)
    year = 2021 - year
    year = year / 2021
    data['year'] = year 
    
    km  = input("Enter the kilometer driven for the Car： (eg. 35000)", type = NUMBER)
    data['km_driven'] = km
    
    fuel_type = radio("Select the fuel type for the Car：", options = ['Diesel','Petrol','CNG','LPG'])
    data['fuel'] = fuel_type
    
    seller_type = radio("Select the seller type for the Car：", options = ['Individual','Dealer','Trustmark Dealer'])
    data['seller_type'] = seller_type
    
    transmission = radio("Select the gear type for the Car：", options = ['Manual','Automatic'])
    
    if transmission == 'Manual':
        transmission = 0
    else :
        transmission = 1
    
    data['transmission'] = transmission
    
    owner = radio("Select the owner type for the Car：", options = ['First Owner','Second Owner','Third Owner','Fourth & Above Owner','Test Drive Car'])
    data['owner'] = owner
    
    mileage  = input("Enter the mileage of the Car (in kmpl)： (eg. 25.17)", type = FLOAT)
    data['mileage'] = mileage
    
    engine  = input("Enter the engine of the Car (in CC)：  (eg. 799)", type = NUMBER)
    data['engine'] = engine
    
    max_power  = input("Enter the max power of the Car (in bhp)： (eg. 53.3)", type = FLOAT)
    data['max_power'] = max_power
    
    seats = select("Select the number of seats for the Car：",seat_no)
    data['seats'] = seats
    
    torque = input("Enter the torque for the Car： (eg. 72Nm@ 4386-5500rpm)", type = TEXT)
    
    def preprocess_torque(s):
        l = re.findall(r"\d*\.\d+|\d+", s)
        return ' '.join(l)
    
    torque = preprocess_torque(torque)
    
    torque_NM = float(torque.split(" ")[0])
    data['torque_NM'] = float(torque_NM)
    
    torque_rpm = float(torque.split(" ")[1])
    data['torque_rpm'] = float(torque_rpm)
    
    cat_columns=['name','fuel','seller_type','owner']
    data[cat_columns]= encoder.transform(data[cat_columns])
    
    num_columns=['km_driven','mileage','engine','max_power','torque_NM','torque_rpm']
    data[num_columns]= scaler.transform(data[num_columns])
    
    prediction = etree.predict(data)
        
    put_text('Predicted Selling Price of the Car is :',round(prediction[0]))
    
    
app.add_url_rule('/tool', 'webio_view', webio_view(predict_price),methods=['GET', 'POST', 'OPTIONS'])   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(predict_price, port=args.port) 