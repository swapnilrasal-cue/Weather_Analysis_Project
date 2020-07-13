from flask import Flask,render_template, request,flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime,date
import datetime 
import uuid
from functools import wraps
from setting import SECRET_KEY,conn
import requests
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from apscheduler.schedulers.background import BackgroundScheduler
import time
from flask_marshmallow import Marshmallow



app = Flask(__name__)

app.config['SECRET_KEY']=SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI']= conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

# models for tables in database
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(255))
    password=db.Column(db.String(255))
    public_id=db.Column(db.String(255))
    
    def __repr__(self):
        return"id:{0} | email:{1}".format(self.id,self.email)

class Weather(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    city_name = db.Column(db.String(30))
    description = db.Column(db.String(30))
    icon = db.Column(db.String(30))
    main = db.Column(db.String(30))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    timezone = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    date = db.Column(db.Date)
    time = db.Column(db.Time)

# Schema for Serialization
class WeatherSchema(ma.Schema):
    class Meta:
        fields = ("id","city_name","description","icon","main","temperature",
        "humidity","timezone","wind_speed","date","time")

weather_schema = WeatherSchema()
weathers_schema = WeatherSchema(many=True)

# created decorator for token validation
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


# this is registration page route
@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    hash_password = generate_password_hash(data['password'],method='sha256')
    new_user=User(email=data['email'],password=hash_password,public_id=str(uuid.uuid4()))
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message':'new user created !'})
  

# this is login page route
@app.route('/login', methods=('GET', 'POST'))
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Please fill Username and Password !",401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return make_response("User Not Registered !",401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'password': user.password,'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token':token.decode("UTF-8")})
    
    return make_response("Invalid Credentials !",401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

# this route is to display weather based on city name
@app.route('/weather/<string:city_name>')
@token_required
def weather_analysis_by_name(city_name):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city_name+'&appid=dc04dba2f5a63bbfb99a116f3f6bdf18')
    json_object = r.json()   
    return jsonify({'message': json_object})

# this route is to display weather based on perticullar date
@app.route('/weather/date/<string:cdate>')
# @token_required
def weather_analysis_by_date(cdate):
    print(date)
    weather_details=Weather.query.filter_by(date=str(cdate)).all()
    print(weather_details)
    output=weathers_schema.dump(weather_details)
    if output==[]:
        return jsonify({'Weather Details':'no records found'})
    else:
        return jsonify({'Weather Details':output})
    # return jsonify({'message': 'weather'})

# this route is to display weather all weather update.
@app.route('/weather')
@token_required
def get_weather_details():
    weather_details=Weather.query.all()
    output=weathers_schema.dump(weather_details)
    return jsonify({'Weather Details':output})

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
    
    new_weather_record = Weather(city_name=city_name,description=description,icon=icon,
    main=main,temperature=temperature,humidity=humidity,timezone=timezone,wind_speed=wind_speed,
    date=today,time=current_time)
    
    db.session.add(new_weather_record)
    db.session.commit()
    print("added current weather update ")


if __name__ == "__main__":
    # this manager.run() can be used only for migrate and upgrade database
    # manager.run()
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_current_weather, 'interval', minutes=60)
    scheduler.start()
    app.run(debug=True)