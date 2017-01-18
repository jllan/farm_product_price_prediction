from app import db
from flask_mongoengine.wtf import model_form

class Prices(db.Document):
    title = db.StringField()
    price = db.StringField()
    date = db.StringField()
    market = db.StringField()

PriceForm = model_form(Prices)