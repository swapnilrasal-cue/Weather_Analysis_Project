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
import logging


api = Api(app)
logging.basicConfig(level=logging.DEBUG)


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
# @token_required
def index():
    app.logger.info('Processing default request')
    app.logger.info('Completed Processing.')
    return jsonify({'message':'Welcome to Weather Analysis App .'})
    

class UserAPI(Resource):
    # this is login page route
    def get(self):
        try:
            app.logger.info('Processing default request')

            auth = request.authorization
            app.logger.info('succesfully got auth info.')

            if not auth or not auth.username or not auth.password:
                app.logger.info('failed to log in.') 
                failureMessage = {'message': 'Username and Password Fields are Required !',
                'code': 'FAILURE'}
                app.logger.info('Completed Processing.')
                return make_response(jsonify(failureMessage), 406)

            user = models.User.query.filter_by(email=auth.username).first()

            if not user:
                app.logger.info('failed to log in.')
                failureMessage = {
                'message': 'The email address that you have  entered does not match any account. Register for an account.',
                'code': 'FAILURE'
                }
                app.logger.info('Completed Processing.')
                return make_response(jsonify(failureMessage), 404)

            if check_password_hash(user.password, auth.password):
                token = jwt.encode({'password': user.password,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                app.config['SECRET_KEY'])
                successMessage = {'message': 'Logged in Successfully !',
                'code': 'SUCCESS','x-access-token':token.decode("UTF-8")}
                app.logger.info('Login Successfull.')
                app.logger.info('Completed Processing.')
                return make_response(jsonify(successMessage), 202)
        
            app.logger.info('failed to log in.')
            failureMessage = {
                'message': 'Invalid Credentials !',
                'code': 'FAILURE'
                }
            
            app.logger.info('Completed Processing.')
            return make_response(jsonify(failureMessage), 401)
    
        except Exception as e:
            return jsonify({'Exception':e})


    def post(self):
        try:
            app.logger.info('Processing default request')

            data = request.get_json()
            
            user = models.User.query.filter_by(email=data['email']).first()
            if user:
                app.logger.info('Signup Failed.')
                app.logger.info('.')
                failureMessage = {
                'message': 'Email Already Exist.',
                'code': 'FAILURE'                
                }
                app.logger.info('Completed Processing.')
                return make_response(jsonify(failureMessage), 400)
  
            hash_password = generate_password_hash(data['password'],method='sha256')
            new_user=models.User(email=data['email'],password=hash_password,public_id=str(uuid.uuid4()))
            models.db.session.add(new_user)
            models.db.session.commit()    
            successMessage = {'message': 'User Successfully Created', 'code': 'SUCCESS'}
            app.logger.info('Signup Successfully.')
            app.logger.info('Completed Processing.')
            return make_response(jsonify(successMessage), 201)
        
        except Exception as e:
            return jsonify({'Exception':e})

    
api.add_resource(UserAPI, '/users')


# this route is to display weather based on city name
@app.route('/weather/<string:city_name>')
# @token_required
def weather_analysis_by_name(city_name):
    try:
        app.logger.info('Processing default request')

        r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city_name+'&appid=dc04dba2f5a63bbfb99a116f3f6bdf18')
        json_object = r.json()   

        app.logger.info('Weather is Displayed.')
        app.logger.info('Completed Processing.')

        return make_response(jsonify(json_object), 302)

    except Exception as e:
        return jsonify({'Exception':e})

# this route is to display the weather recorded on perticular date.
@app.route('/weather/date/<string:cdate>')
# @token_required
def weather_analysis_by_date(cdate):
    try:
        app.logger.info('Processing default request')

        weather_details=models.Weather.query.filter_by(date=str(cdate)).all()
        output=models.weathers_schema.dump(weather_details)
        if output==[]:
            app.logger.info('No record found for this date.')

            failureMessage = {
            'message': 'No Records Found.',
            'code': 'FAILURE'
            }
            app.logger.info('Completed Processing.')
            return make_response(jsonify(failureMessage), 404)
        else:
            app.logger.info('Record Displayed.')
            app.logger.info('Completed Processing.')            
            return make_response(jsonify(output), 302)    

    except Exception as e:
        return jsonify({'Exception':e})

# this route is to display weather all weather update.
@app.route('/weather')
@token_required
def get_weather_details():
    try:
        app.logger.info('Processing default request')
        weather_details=models.Weather.query.all()
        output=models.weathers_schema.dump(weather_details)
        app.logger.info('Completed Processing.')
        return make_response(jsonify(output), 302)
    
    except Exception as e:
        return jsonify({'Exception':e})


# function to fetch weather details from api every hour and save it in database 
def get_current_weather():
    try:
        app.logger.info('Processing default request')
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
        print("Current weather update added to database.")
        app.logger.info('Completed Processing.')

    except Exception as e:
        return jsonify({'Exception':e})
