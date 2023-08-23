#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)

class Campers(Resource):
    def get(self):
        campers = [c.to_dict(rules=("-signups",)) for c in Camper.query.all()]
        return make_response(campers, 200)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(**data)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.add(new_camper)
        db.session.commit()
        return make_response(new_camper.to_dict(rules=("-signups",)), 201)

api.add_resource(Campers, "/campers")

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(rules=("-signups.activity.signups",)), 200)

    def patch(self, id):
        data = request.get_json()
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        try:
            for attr, value in data.items():
                setattr(camper, attr, value)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.add(camper)
        db.session.commit()
        return make_response(camper.to_dict(rules=("-signups",)), 202)

api.add_resource(CamperById, "/campers/<int:id>")

class Activities(Resource):
    def get(self):
        activities = [a.to_dict(rules=("-signups",)) for a in Activity.query.all()]
        return make_response(activities, 200)

api.add_resource(Activities, "/activities")

class AcivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response("", 204)

api.add_resource(AcivityById, "/activities/<int:id>")

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(**data)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.add(new_signup)
        db.session.commit()
        return make_response(
            new_signup.to_dict(
                rules=(
                    "-camper.signups",
                    "-activity.signups",
                )
            ),
            201,
        )

api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)