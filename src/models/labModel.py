from src import db
import time
class LabInventory(db.Document):
    name=db.StringField()
    price=db.StringField()
    

class LabInvoice(db.Document):
    date = time.strftime("%H:%M:%S", time.localtime() ) 
    items = []
    total = db.StringField()
    