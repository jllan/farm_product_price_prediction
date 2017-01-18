from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object('config')
# app.config['MONGODB_SETTINGS'] = {'db': 'todo'}
db = MongoEngine(app)

from app import view