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
from models import db, User, Character, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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

# USER FUNCTIONS
@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    all_users_list = list(map(lambda user: user.serialize(),all_users))

    return jsonify(all_users_list), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.json
    required_properties = ["email", "first_name", "last_name", "password", "username"]

    for prop in required_properties:
        if prop not in user_data: return f"The '{prop}' property of the user was not properly written", 400 

    user_to_add = User(**user_data)
    db.session.add(user_to_add)
    db.session.commit()

    return "User created properly", 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def del_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user_to_delete = user.serialize()
    user_name = user_to_delete["first_name"]
    db.session.delete(user)
    db.session.commit()

    return f"The user '{user_name}' deleted successfully", 200

# CHARACTER FUNCTIONS
@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Character.query.all()
    all_characters_list = list(map(lambda character: character.serialize(),all_characters))

    return jsonify(all_characters_list), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    return jsonify(character.serialize()), 200

@app.route('/characters', methods=['POST'])
def add_character():
    character_data = request.json
    required_properties = ["name", "specie", "height", "gender"]

    for prop in required_properties:
        if prop not in character_data: return f"The '{prop}' property of the Character was not properly written", 400 

    character_to_add = Character(**character_data)
    db.session.add(character_to_add)
    db.session.commit()

    return "Character created properly", 200

@app.route('/characters/<int:character_id>', methods=['DELETE'])
def del_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    character_to_delete = character.serialize()
    character_name = character_to_delete["name"]
    db.session.delete(character)
    db.session.commit()

    return f"The character '{character_name}' disappeared into the galaxy", 200

# PLANET FUNCTIONS
@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    all_planets_list = list(map(lambda planet: planet.serialize(),all_planets))

    return jsonify(all_planets_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()

    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def add_planets():
    planet_data = request.json
    required_properties = ["name", "diameter", "terrain", "population"]

    for prop in required_properties:
        if prop not in planet_data: return f"The '{prop}' property of the Planet was not properly written", 400 

    planet_to_add = Planet(**planet_data)
    db.session.add(planet_to_add)
    db.session.commit()

    return "Planet created properly", 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    planet_to_delete = planet.serialize()
    planet_name = planet_to_delete["name"]
    db.session.delete(planet)
    db.session.commit()

    return f"The planet '{planet_name}' was destroyed for the Empire successfully", 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
