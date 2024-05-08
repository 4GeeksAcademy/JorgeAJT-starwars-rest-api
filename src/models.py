from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), unique=False, nullable=True)
    last_name = db.Column(db.String(120), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            # do not serialize the password, its a security breach
        }
    
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    specie = db.Column(db.String(50), unique=False, nullable=False)
    height = db.Column(db.String(20), unique=False, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)

    def __repr__(self):
        return f"<Character {self.id}>"

    def serialize(self):
        return {
            "name": self.name,
            "specie": self.specie,
            "height": self.height,
            "gender": self.gender,
            "id": self.id,
        }
    
class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    population = db.Column(db.String(50), unique=False, nullable=False)
    terrain = db.Column(db.String(100), unique=False, nullable=False)
    diameter = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return f"<Planet {self.id}>"

    def serialize(self):
        return {
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain,
            "diameter": self.diameter,
            "id": self.id,
        }