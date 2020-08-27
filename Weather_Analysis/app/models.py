from app import app
from flask_sqlalchemy import SQLAlchemy
from setting import SECRET_KEY,conn
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_marshmallow import Marshmallow


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

