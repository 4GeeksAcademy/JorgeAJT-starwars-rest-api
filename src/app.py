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
from models import db, User, Character, Planet, Character_fav, Planet_fav
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

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.json
    required_properties = ["email", "password", "username", "is_active"]

    for prop in required_properties:
        if prop not in user_data: return jsonify({"Error": f"The '{prop}' property of the user is not or is not properly written"}), 400    
        existing_email = User.query.filter_by(email=user_data["email"]).first()
        if existing_email: return jsonify({"Error": f"The email '{existing_email.email}' is already registered in the database"}), 400
        existing_username = User.query.filter_by(username=user_data["username"]).first()
        if existing_username: return jsonify({"Error": f"The username '{existing_username.username}' is already registered in the database"}), 400      

    for prop in required_properties:
        for key in user_data:
            if prop == key and user_data[key] == "": return jsonify({"Error": f"The value of '{key}' must not be empty"}), 400

    user_to_add = User(**user_data)
    db.session.add(user_to_add)
    db.session.commit()

    return jsonify(user_to_add.serialize()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def del_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user: return jsonify({"Error": "This user's ID does not exist in the database"}), 400
    user_to_delete = user.serialize()
    user_name = user_to_delete["first_name"]
    db.session.delete(user)
    db.session.commit()

    return jsonify({"Deleted": f"The user '{user_name}' was eradicated successfully"}), 200

# FAVORITES
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    fav_characters = Character_fav.query.filter_by(user_id=user_id).all()
    fav_planets = Planet_fav.query.filter_by(user_id=user_id).all()
    favorites = fav_characters + fav_planets
    serialized_favorites = list(map(lambda fav: fav.serialize(), favorites))

    return jsonify(serialized_favorites), 200

@app.route('/users/<int:user_id>/favorites/characters', methods=['POST'])
def add_favorites_characters(user_id):
    id_data = request.json
    character_id = id_data["character_id"]
    required_properties = ["user_id", "character_id"]

    for prop in required_properties:
        if prop not in id_data: return jsonify({"Error": f"The '{prop}' property was not properly written"}), 400

    for key in id_data:
        if id_data[key] == "": return jsonify({"Error": f"The value of '{key}' must not be empty"}), 400

    existing_favorite = Character_fav.query.filter_by(character_id=character_id, user_id=user_id).first()
    if existing_favorite: 
        serialized_existing_favorite = existing_favorite.serialize()
        existing_favorite_name = serialized_existing_favorite["character_name"]
        return jsonify({"Error": f"The ID {character_id} is already in the favorites list and belongs to the powerful {existing_favorite_name}"}), 400

    searching_character = Character.query.filter_by(id=character_id).first()
    if not searching_character: return jsonify({"Error": f"The ID {character_id} does not belong to any character"}), 400

    new_character_fav = Character_fav(character_id=character_id, user_id=user_id)
    db.session.add(new_character_fav)
    db.session.commit()

    return jsonify(new_character_fav.serialize()), 200

@app.route('/users/<int:user_id>/favorites/characters/<int:general_id>', methods=['DELETE'])
def del_favorite_character(user_id, general_id):
    character = Character_fav.query.filter_by(id=general_id).first()
    if not character: return jsonify({"Error": f"The ID introduced does not exist in the favorite list"}), 400
    character_to_delete = character.serialize()
    character_name = character_to_delete["character_name"]
    db.session.delete(character)
    db.session.commit()

    return jsonify({"Deleted": f"The character '{character_name}' disappeared from the FAVORITE galaxy"}), 200

@app.route('/users/<int:user_id>/favorites/planets', methods=['POST'])
def add_favorites_planets(user_id):
    id_data = request.json
    planet_id = id_data["planet_id"]
    required_properties = ["user_id", "planet_id"]

    for prop in required_properties:
        if prop not in id_data: return jsonify({"Error": f"The '{prop}' property was not properly written"}), 400

    for key in id_data:
        if id_data[key] == "": return jsonify({"Error": f"The value of '{key}' must not be empty"}), 400

    existing_favorite = Planet_fav.query.filter_by(planet_id=planet_id, user_id=user_id).first()
    if existing_favorite: 
        serialized_existing_favorite = existing_favorite.serialize()
        existing_favorite_name = serialized_existing_favorite["planet_name"]
        return jsonify({"Error": f"The ID {planet_id} is already in the favorites list and belongs to the amazing {existing_favorite_name}"}), 400

    searching_planet = Planet.query.filter_by(id=planet_id).first()
    if not searching_planet: return jsonify({"Error": f"The ID {planet_id} does not belong to any planet"}), 400

    new_planet_fav = Planet_fav(planet_id=planet_id, user_id=user_id)
    db.session.add(new_planet_fav)
    db.session.commit()

    return jsonify(new_planet_fav.serialize()), 200

@app.route('/users/<int:user_id>/favorites/planets/<int:general_id>', methods=['DELETE'])
def del_favorite_planets(user_id, general_id):
    planet = Planet_fav.query.filter_by(id=general_id).first()
    if not planet: return jsonify({"Error": f"The ID introduced does not exist in the favorite list"}), 400
    planet_to_delete = planet.serialize()
    planet_name = planet_to_delete["planet_name"]
    db.session.delete(planet)
    db.session.commit()

    return jsonify({"Deleted": f"The planet '{planet_name}' disappeared from the FAVORITE galaxy"}), 200

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
        if prop not in character_data: return jsonify({"Error": f"The '{prop}' property of the character is not or is not properly written"}), 400

    for key in character_data:
        if character_data[key] == "": return jsonify({"Error": f"The value of '{key}' must not be empty"}), 400

    character_duplicate = Character.query.filter_by(name=character_data["name"]).first()
    if character_duplicate: return jsonify({"Error": "This character's name already exists in the database"}), 400

    character_to_add = Character(**character_data)
    db.session.add(character_to_add)
    db.session.commit()

    return jsonify(character_to_add.serialize()), 200

@app.route('/characters/<int:character_id>', methods=['DELETE'])
def del_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    if not character: return jsonify({"Error": "This character's ID does not exist in the database"}), 400
    character_to_delete = character.serialize()
    character_name = character_to_delete["name"]
    db.session.delete(character)
    db.session.commit()

    return jsonify({"Deleted": f"The character '{character_name}' disappeared from the galaxy"}), 200

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
        if prop not in planet_data: return jsonify({"Error": f"The '{prop}' property of the planet is not properly written"}), 400

    for key in planet_data:
        if planet_data[key] == "": return jsonify({"Error": f"The value of '{key}' must not be empty"}), 400

    planet_duplicate = Planet.query.filter_by(name=planet_data["name"]).first()
    if planet_duplicate: return jsonify({"Error": "This planet's name already exists in the database"}), 400

    planet_to_add = Planet(**planet_data)
    db.session.add(planet_to_add)
    db.session.commit()

    return jsonify(planet_to_add.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    if not planet: return jsonify({"Error": "This planet's ID does not exist in the database"}), 400
    planet_to_delete = planet.serialize()
    planet_name = planet_to_delete["name"]
    db.session.delete(planet)
    db.session.commit()

    return jsonify({"Deleted": f"The planet '{planet_name}' was destroyed for the Empire successfully"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
