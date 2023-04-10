#!/usr/bin/env python3

import os  
from flask import Flask, jsonify, make_response, request, g, current_app, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import json
from flask_restful import Api, Resource
from sqlalchemy_serializer import SerializerMixin

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Index(Resource):
    def get(self):
        response_dict = {"message": "Hello Scientists!"}
        return make_response(jsonify(response_dict), 200)

api.add_resource(Index, '/')

class Scientists(Resource):
    def get(self):
        response_dict_list = [n.to_dict(only=('id', 'name', 'field_of_study', 'avatar')) for n in Scientist.query.all()]
        return make_response(jsonify(response_dict_list), 200)
    
    def post(self):
        try:
            new_record = Scientist(
                name=request.form.get('name'),
                field_of_study= request.form.get('field_of_study'),
                avatar=request.form.get('avatar'), 
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_record.to_dict()), 201)
        return response 

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        res = Scientist.query.filter_by(id=id).first()
        if res:
            response_dict = res.to_dict()
            return make_response(response_dict, 200)
        return make_response(jsonify({"error": "Scientist not found"}), 404)
    
    def patch(self, id):
        record = Scientist.query.filter(Scientist.id == id).first()
        if record:
            try:
                for attr in request.form:
                    setattr(record, attr, request.form.get(attr))
                db.session.add(record)
                db.session.commit()
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response = make_response(jsonify(record.to_dict()), 201)
            return response 
        return make_response(jsonify({"error": "Scientist not found"}), 404)
    
    def delete(self, id):
        record = Scientist.query.filter(Scientist.id == id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            response_dict = {"message": "Record successfully deleted"}
            return make_response(jsonify(response_dict), 200)
        return make_response(jsonify({"error": "Scientist not found"}), 404)
    
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        response_dict_list = [n.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star', 'image')) for n in Planet.query.all()]
        return make_response(jsonify(response_dict_list), 200)

api.add_resource(Planets, '/planets')

class Missions(Resource):
    def get(self):
        response_dict_list = [n.to_dict(only=('id', 'name', 'scientist_id', 'planet_id')) for n in Mission.query.all()]
        return make_response(jsonify(response_dict_list), 200)
    
    def post(self):
        try:
            new_record = Mission(
                name=request.form.get('name'),
                scientist_id=int(request.form.get('scientist_id')),
                planet_id=int(request.form.get('planet_id')), 
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_record.planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star', 'image'))), 201)
        return response 

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555)

