from src import db

class User(db.Document):
    name = db.StringField( max_length=50)
    email = db.StringField( max_length=50, unique=True)
    password = db.StringField( max_length=500)
    dept = db.StringField()
    
   