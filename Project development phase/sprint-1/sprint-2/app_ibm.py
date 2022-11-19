import os
import json
import joblib
import requests 
from chronic_pred import User
from flask_mail import Message
from chronic_pred import app, db, bcrypt, mail
from oauthlib.oauth2 import WebApplicationClient
from flask import Flask,render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from chronic_pred.forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm


app = Flask(__name__)
app.debug = True
API_KEY = "_YBwCIVTCKowMStvz4HHQTcizrYGJUV0p9bj_W4uzh3-"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
app.config['SECRET_KEY'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'




@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
@login_required
def predict():
    return render_template('prediction.html')


@app.route('/result', methods=['GET','POST'])
def result():
    if request.method == 'POST':
        age = int(request.form['age'])
        usg = float(request.form['usg'])
        sal = float(request.form['sal'])
        bp = float(request.form['bp'])
        su = float(request.form['su'])
        bu = float(request.form['bu'])
        sc = float(request.form['sc'])
        sod = float(request.form['sod'])
        pot = float(request.form['pot'])
        hg = float(request.form['hg'])
        pcv = int(request.form['pcv'])
        wbcc = float(request.form['wbcc'])
        diab = str(request.form['diab'])
        diab = 1 if diab == 'yes' else 0
        cad = str(request.form['cad'])
        cad = 1 if cad == 'yes' else 0
        hp = str(request.form['hp'])
        hp = 1 if hp == 'yes' else 0
        
        payload_scoring = {
        "input_data": [{"field": [["bp", "usg", "sal"," su", "bu", "sc", "sod", "pot", "hg", "pcv", "wbcc", "diab", "cad", "hp" ,"age"]], "values": [[bp, usg, sal, su, bu, sc, sod, pot, hg, pcv, wbcc, diab, cad, hp ,age]]}]
}
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/c987d410-9ac4-4691-9ddf-cbb42f7b4516/predictions?version=2022-11-13', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        #print("Scoring response")
        predictions = response_scoring.json()
        print("Scoring response")
        print(response_scoring.json())
        predict = predictions["predictions"][0]["values"][0][0]
        if predict == 1:
            return render_template('negative.html')
        else:
            return render_template('positive.html')


if __name__ == '__main__':

    app.run(debug=True)