import json
import requests 
from chronic_pred import User
from flask_mail import Message
from oauthlib.oauth2 import WebApplicationClient
from chronic_pred import app, db, bcrypt, mail
from chronic_pred import mltoken
from flask import render_template, url_for, flash, redirect, request
from chronic_pred.forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/links")
@login_required
def useful_links():
    return render_template('blog.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

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
        X = [[age, usg, sal, bp, su, bu, sc, sod, pot, hg, pcv, wbcc, diab, cad, hp]]
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

