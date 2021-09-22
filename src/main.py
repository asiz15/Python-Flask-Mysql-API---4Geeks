"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/api/people')
def get_people():
    people = People.query.all()
    people = list(map(lambda p: p.serialize(), people))
    return jsonify(people)

@app.route('/api/people/<int:id>',methods=['GET'])
def get_people_by_id(id):
    people = People.query.get(id)
    if not people: return jsonify({"message": "There is not characters with this id", "status_code": 400}),400
    return jsonify(people.serialize())

@app.route('/api/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets = list(map(lambda p: p.serialize(), planets))
    return jsonify(planets)

@app.route('/api/planets/<int:id>',methods=['GET'])
def get_planet(id):
    planet = Planet.query.get(id)
    if not planet: return jsonify({"message": "There is not planet with this id", "status_code": 400}),400
    return jsonify(planet.serialize())

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users = list(map(lambda u: u.serialize(),users))

    return jsonify(users)

@app.route('/api/users/favorites', methods=['GET'])
def get_user_favorites():
    users = User.query.all()
    users = list(map(lambda x: x.with_favorites(), users))
    return jsonify(users)

@app.route('/api/favorite/planet/<int:id>', methods=['POST'])
def set_favorite_planet(id):
    user = User.query.get(1)
    planet = Planet.query.get(id)
    if not user: return jsonify({ "message": 'There is no user with this id', "status_code": 400 }),400
    if not planet: return jsonify({ "message": 'There is no planet with this id', "status_code": 400 }),400

    user.favorites_planets.append(planet)
    user.save()
    return jsonify({"message": "Success!", "data": user.with_favorites()})

@app.route('/api/favorite/people/<int:id>', methods=['POST'])
def set_favorite_people(id):
    user = User.query.get(1)
    people = People.query.get(id)
    if not user: return jsonify({ "message": 'There is no user with this id', "status_code": 400 }),400
    if not people: return jsonify({ "message": 'There is no characters with this id', "status_code": 400 }),400

    user.favorites_people.append(people)
    user.save()
    return jsonify({"message": "Success!", "data": user.with_favorites()})

@app.route('/api/favorite/planet/<int:id>', methods=['DELETE'])
def delete_favorite_planet(id):
    user = User.query.get(1)
    planet = Planet.query.get(id)
    if not user: return jsonify({ "message": 'There is no user with this id', "status_code": 400 }),400
    if not planet: return jsonify({ "message": 'There is no planet with this id', "status_code": 400 }),400

    user.favorites_planets.remove(planet)
    user.save()
    return jsonify({"message": "Delete success!", "data": user.with_favorites()})

@app.route('/api/favorite/people/<int:id>', methods=['DELETE'])
def delete_favorite_people(id):
    user = User.query.get(1)
    people = People.query.get(id)
    if not user: return jsonify({ "message": 'There is no user with this id', "status_code": 400 }),400
    if not people: return jsonify({ "message": 'There is no characters with this id', "status_code": 400 }),400

    user.favorites_people.remove(people)
    user.save()
    return jsonify({"message": "Delete success!", "data": user.with_favorites()})
# this only runs if `$ python src/main.py` is executed


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
