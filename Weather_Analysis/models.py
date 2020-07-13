# from flask_sqlalchemy import SQLAlchemy


# db = SQLAlchemy()

# class User(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     email=db.Column(db.String(255))
#     password=db.Column(db.String(255))
#     public_id=db.Column(db.String(255))
    
#     def __repr__(self):
#         return"id:{0} | email:{1}".format(self.id,self.email)

# class Weather(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     city_name=db.Column(db.String(30))
#     temperature=db.Column(db.Float)
#     humidity=db.Column(db.Float)
    
    
#     def __repr__(self):
#         return"id:{0} | email:{1}".format(self.id,self.email)
