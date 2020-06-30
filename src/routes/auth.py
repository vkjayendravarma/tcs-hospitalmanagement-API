from src import app,db,Config
from flask import request
from src.models import usersModel
from flask_mongoengine import mongoengine
import bcrypt
# from flask_jwt import JWT, jwt_required, current_identity
import jwt
import datetime



@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form.get('password').encode("UTF-8")
    accessLevel = request.form['accessLevel']
    
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    
    try:        
        usersModel.User(name=name, email=email, password=password, accessLevel=accessLevel).save()
    except mongoengine.errors.NotUniqueError as e:
        print(e)
        return str(e)
    
    return "None"

@app.route('/login', methods=['POST'])
def login():
    email= request.form['email']
    password= request.form.get('password').encode("UTF-8")
    
    user = usersModel.User.objects(email=email).first()
    if(user):
        print(user)
        if(bcrypt.checkpw(password, user.password.encode("UTF-8"))):
            token = jwt.encode({'user': {
                "userID": "user['_id']",
                "level": user.accessLevel
                }, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, Config.SECRET_KEY)
            return {
                "success": True,
                "token": token.decode('UTF-8')                
            }
        else:
            return "failed"
        
    else:
        return "No"
		