from app import app
from app import models
from flask import Flask,render_template, request,flash, make_response, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime,date
import datetime
from functools import wraps
import time
import requests
import uuid
from setting import SECRET_KEY
from flask_restful import Api, Resource

api = Api(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is Missing, Unauthorised User'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'Token is Invalid'}),401

        return f(*args, **kwargs)
    
    return decorated


# this is home page route
@app.route('/home')
@token_required
def index():
    return jsonify({'message':'Welcome to Weather Analysis App .'})


class UserAPI(Resource):
    # this is login page route
    def get(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            failureMessage = {'message': 'Username and Password Fields are Required !',
            'code': 'FAILURE'}
            return make_response(jsonify(failureMessage), 406)

        user = models.User.query.filter_by(email=auth.username).first()

        if not user:
            failureMessage = {
            'message': 'The email address that you have  entered does not match any account. Register for an account.',
            'code': 'FAILURE'
            }
            return make_response(jsonify(failureMessage), 404)

        if check_password_hash(user.password, auth.password):
            token = jwt.encode({'password': user.password,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'])
            successMessage = {'message': 'Logged in Successfully !',
            'code': 'SUCCESS','x-access-token':token.decode("UTF-8")}
            return make_response(jsonify(successMessage), 202)
        
        failureMessage = {
            'message': 'Invalid Credentials !',
            'code': 'FAILURE'
            }
        return make_response(jsonify(failureMessage), 401)

    def post(self):
        data = request.get_json()
        user = models.User.query.filter_by(email=data['email']).first()
        if user:
            failureMessage = {
            'message': 'Email Already Exist.',
            'code': 'FAILURE'
            }
            return make_response(jsonify(failureMessage), 400)
  
        hash_password = generate_password_hash(data['password'],method='sha256')
        new_user=models.User(email=data['email'],password=hash_password,public_id=str(uuid.uuid4()))
        models.db.session.add(new_user)
        models.db.session.commit()    
        successMessage = {'message': 'User Successfully Created', 'code': 'SUCCESS'}
        return make_response(jsonify(successMessage), 201)

    
api.add_resource(UserAPI, '/users')


# this route is to display weather based on city name
@app.route('/weather/<string:city_name>')
@token_required
def weather_analysis_by_name(city_name):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city_name+'&appid=dc04dba2f5a63bbfb99a116f3f6bdf18')
    json_object = r.json()   
    return make_response(jsonify(json_object), 302)

# this route is to display the weather recorded on perticular date.
@app.route('/weather/date/<string:cdate>')
@token_required
def weather_analysis_by_date(cdate):
    weather_details=models.Weather.query.filter_by(date=str(cdate)).all()
    output=models.weathers_schema.dump(weather_details)
    if output==[]:
        failureMessage = {
            'message': 'No Records Found.',
            'code': 'FAILURE'
        }
        return make_response(jsonify(failureMessage), 404)
    else:
        return make_response(jsonify(output), 302)    


# this route is to display weather all weather update.
@app.route('/weather')
@token_required
def get_weather_details():
    weather_details=models.Weather.query.all()
    output=models.weathers_schema.dump(weather_details)
    return make_response(jsonify(output), 302)

# function to fetch weather details from api every hour and save it in database 
def get_current_weather():
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Pune&appid=dc04dba2f5a63bbfb99a116f3f6bdf18')
    json_object = r.json()
    
    city_name = json_object['name']     
    weather = json_object['weather']
    description = weather[0]['description']
    icon = weather[0]['icon']
    main = weather[0]['main']
    temperature = float(json_object['main']['temp'])
    humidity = float(json_object['main']['humidity'])
    timezone = json_object['timezone']
    wind_speed = float(json_object['wind']['speed'])
    today = date.today()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    
    new_weather_record = models.Weather(city_name=city_name,description=description,icon=icon,
    main=main,temperature=temperature,humidity=humidity,timezone=timezone,wind_speed=wind_speed,
    date=today,time=current_time)
    
    models.db.session.add(new_weather_record)
    models.db.session.commit()
    print("added current weather update ")
