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


GOOGLE_CLIENT_ID = "660143345755-c53v3c2qe7ejoj0r0vc9op5am8hksv82.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

def send_conf_email(user):
    token = user.get_reset_token()
    msg = Message('Confirmation Mail',
                  sender='kidney.disease.predictor@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Your account was successfully created. Please click the link below to confirm your email address and activate your account:

{url_for('register_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/Register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        send_conf_email(user)
        flash('An email has been sent with instructions to confirm your account.', 'info')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)

@app.route("/Register/<token>", methods=['GET', 'POST'])
def register_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('register'))
    user.email_confirmed = True
    db.session.commit()
    flash('Your email is verified! You are now able to log in', 'success')
    return redirect(url_for('login'))
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/glogin")
def glogin():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/glogin/callback")
def callback():
    
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

   
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["name"]
    else:
        return "User email not available or not verified by Google.", 400
    password =  bcrypt.generate_password_hash(users_name).decode('utf-8') 
    user = User(
        username=users_name, email=users_email,email_confirmed=True,password = password
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return redirect(url_for("home"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()