#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    camper_data = [{'id': c.id, 'name': c.name, 'age': c.age} for c in campers]
    return jsonify(camper_data)

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)
    if camper is None:
        return jsonify({'error': 'Camper not found'}), 404
    
    camper_data = camper.to_dict(exclude=['signups'])
    camper_data['signups'] = []
    for signup in camper.signups:
        signup_data = signup.to_dict()
        signup_data['activity'] = signup.activity.to_dict(exclude=['campers'])
        camper_data['signups'].append(signup_data)

    return jsonify(camper_data)

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    data = request.get_json()
    camper = Camper.query.get(id)
    if camper is None:
        return jsonify({'error': 'Camper not found'}), 404
    
    if 'name' in data:
        camper.name = data['name']
    if 'age' in data:
        camper.age = data['age']

    try:
        db.session.commit()
        return jsonify(camper.to_dict(exclude=['signups']))
    except:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400
    
@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    if 'name' not in 'data' or 'age' not in data:
        return jsonify({'errors': ['name and age are required fields']}), 400
    
    camper = Camper(name=data['name'], age=data['age'])
    try:
        db.session.add(camper)
        db.session.commit()
        data['id'] = camper.id
        return jsonify(data)
    except:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400
    
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    activity_list = [{'id': activity.id, 'name': activity.name, 'difficulty': activity.difficulty} for activity in activities]
    return jsonify(activity_list)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if activity is None:
        return jsonify({'error': 'Activity not found'}), 404
    
    try:
        db.session.delete(activity)
        db.session.commit()
        return '', 204
    except:
        db.session.rollback()
        return jsonify({'errors': ['An error occured while deleting the activity']}), 500

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    if 'camper_id' not in data or 'activity_id' not in data or 'time' not in data:
        return jsonify({'errors': ['camper_id, activity_id, and time are required fields']}), 400

    camper_id = data['camper_id']
    activity_id = data['activity_id']
    time = data['time']

    camper = Camper.query.get(camper_id)
    activity = Activity.query.get(activity_id)

    if not camper or not activity:
        return jsonify({'errors': ['Camper or Activity not found']}), 400
    
    signup = Signup(camper=camper, activity=activity, time=time)

    try:
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict(related=['activity', 'camper']))
    except:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)