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
from models import db, User, Planet, Favorite, People
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

########## INICIO DE LAS RUTAS DEL EJERCICIO ##########

# RUTAS PARA USUARIO (User)

# [GET] /users Listar todos los usuarios del blog.
# Está ruta la hicimos en grupo (Yenesey-Ricardo-David)


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()

    if not users:
        return jsonify({"mensaje": "Usuarios no encontrados"}), 404

    response_body = {
        "Users": [user.serialize_user() for user in users]
    }

    return jsonify(response_body), 200


# [GET] /users Listar todos los usuarios del blog (aqui tengo dudas)
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify([favorite.serialize() for favorite in user.favorites]), 200


# RUTAS PARA PLANETAS(Planet)

# [GET] /planets Listar todos los registros de planets en la base de datos *
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()

    if not planets:
        return jsonify({"mensaje": "Planetas no encontrados"}), 404

    response_body = {
        "Planets": [planet.serialize_planet() for planet in planets]
    }

    return jsonify(response_body), 200


# [GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404
    return jsonify(planet.serialize()), 200


# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def planet_favorite(planet_id):
    request_data = request.get_json()
    user_id = request_data.get('user_id')

    # Aquí se verifica que el user_id esté presente en la solicitud
    if not request_data or "user_id" not in request_data:
        return jsonify({"error": "Invalido user_id es requerido"}), 400

    # Verificar primero si el usuario y el planeta existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404

    # Verifica si ya existe este favorito, para evitar duplicarlo en la base de datos
    favorite_planet = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id).first()
    if favorite_planet:
        return jsonify({'error': 'Este personaje ya está en favoritos'}), 400

    # Crea un nuevo favorito
    new_favorite_planet = Favorite(user_id=user.id, planet_id=planet.id)

    db.session.add(new_favorite_planet)
    db.session.commit()

    return jsonify(new_favorite_planet.serialize()), 201


# [DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id *
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    request_data = request.get_json()
    user_id = request_data.get('user_id')

    # Aquí se verifica que el user_id esté presente en la solicitud
    if not request_data or "user_id" not in request_data:
        return jsonify({"error": "Invalido user_id es requerido"}), 400

    # Comprobar si el usuario y planeta existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'error': 'Planeta no encontrado'}), 404

    # Busca en el registro de favorito que coincida con el user_id y planet_id
    # Elimina el favorito de la base de datos si lo encuentra
    fav_planet = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not fav_planet:
        return jsonify({'error': 'Favorito no encontrado'}), 404

    # Se confirma la eliminación
    db.session.delete(fav_planet)
    db.session.commit()

    return jsonify({'mensaje': 'Planeta Favorito Eliminado'}), 200


# RUTAS PERSONAJES/PERSONAS(People)

# [GET] /peoples *
@app.route('/peoples', methods=['GET'])
def get_all_peoples():
    peoples = People.query.all()

    if not peoples:
        return jsonify({"mensaje": "Personajes no encontrados"}), 404

    response_body = {
        "peoples": [people.serialize() for people in peoples]
    }

    return jsonify(response_body), 200


# [POST] /favorite/people/<int:people_id> *
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_favorite(people_id):
    request_data = request.get_json()
    user_id = request_data.get('user_id')

    # Aquí se verifica que el user_id esté presente en la solicitud
    if not request_data or "user_id" not in request_data:
        return jsonify({"error": "user_id es requerido"}), 400

    # Verificar primero si el usuario y el personaje existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    people = People.query.get(people_id)
    if not people:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    # Verifica si ya existe este favorito, para evitar duplicarlo en la base de datos
    favorite_people = Favorite.query.filter_by(
        user_id=user.id, people_id=people_id).first()
    if favorite_people:
        return jsonify({'error': 'Este personaje ya está en favoritos'}), 400

    # Crea un nuevo favorito
    new_fav_people = Favorite(user_id=user.id, people_id=people.id)

    db.session.add(new_fav_people)
    db.session.commit()

    return jsonify({"mensaje": "Personaje añadido a favoritos correctamente"}), 201


# [DELETE] /favorite/people/<int:people_id> *
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    request_data = request.get_json()
    user_id = request_data.get('user_id')

    # Aquí se verifica que el user_id esté presente en la solicitud
    if not request_data or "user_id" not in request_data:
        return jsonify({"error": "Invalido user_id es requerido"}), 400

    # Verificar primero si el usuario y el personaje existen
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    people = People.query.get(people_id)
    if not people:
        return jsonify({'error': 'Personaje no encontrado'}), 404

    # Busca en el registro de favorito que coincida con el user_id y people_id
    # Elimina el favorito de la base de datos si lo encuentra
    fav_people = Favorite.query.filter_by(
        user_id=user.id, people_id=people_id).first()
    if not fav_people:
        return jsonify({'error': 'Favorito no encontrado'}), 404

    # Se confirma la eliminación
    db.session.delete(fav_people)
    db.session.commit()

    return jsonify({'mensaje': 'Personaje Favorito Eliminado'}), 200


# EXTRAS # EXTRAS # EXTRAS
# Crea endpoints para agregar (POST), modificar (PUT) y eliminar (DELETE) planets y people

# Post Planets - People
@app.route('/planets', methods=['POST'])
def add_planets():

    request_data = request.json

    if not request_data:
        return jsonify({"error": "Datos del planeta requeridos"}), 400

    new_planet = Planet(
        planet_name=request_data.get("planet_name"),
        diameter=request_data.get("diameter"),
        climate=request_data.get("climate"),
        population=request_data.get("population"),
        gravity=request_data.get("gravity"),
        rotation_period=request_data.get("rotation_period"),
        orbital_period=request_data.get("orbital_period"),
        terrain=request_data.get("terrain")
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"mensaje": "Planeta Creado"}), 201


@app.route('/people', methods=['POST'])
def add_planets():

    request_data = request.json

    if not request_data:
        return jsonify({"error": "Datos del personaje requerido"}), 400

    new_people = People(
        people_name=request_data.get("people_name"),
        height=request_data.get("heigt"),
        weight=request_data.get("weight"),
        hair_color=request_data.get("hair_color"),
        skin_color=request_data.get("skin_color"),
        eye_color=request_data.get("eye_color"),
        birth_day=request_data.get("birth_day"),
        gender=request_data.get("gender"),
        species=request_data.get("species"),
        home_planet=request_data.get("home_planet")
    )

    db.session.add(new_people)
    db.session.commit()

    return jsonify({"mensaje": "Personaje Creado"}), 201

# Put Planets - Peoples
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    request_data = request.json

    if not request_data:
        return jsonify({"error": "Solicitud Invalida"}), 400

    planet = Planet.query.get(planet_id)

    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    planet.planet_name = request_data.get("planet_name", planet.planet_name)
    planet.diameter = request_data.get("diameter", planet.diameter)
    planet.climate = request_data.get("climate", planet.climate)
    planet.population = request_data.get("population", planet.population)
    planet.gravity = request_data.get("gravity", planet.gravity)
    planet.rotation_period = request_data.get(
        "rotation_period", planet.rotation_period)
    planet.orbital_period = request_data.get(
        "orbital_period", planet.orbital_period)
    planet.terrain = request_data.get("terrain", planet.terrain)

    db.session.commit()
    return jsonify({"mensaje": "Planeta actualizado"}), 200


@app.route('/peoples/<int:people_id>', methods=['PUT'])
def update_people(people_id):
    request_data = request.json

    if not request_data:
        return jsonify({"error": "Solicitud Invalida"}), 400

    people = People.query.get(people_id)

    if not people:
        return jsonify({"error": "Personaje no encontrado"}), 404

    people.people_name = request_data.get("people_name", people.people_name)
    people.height = request_data.get("heigt", people.height)
    people.weight = request_data.get("weight", people.weight)
    people.hair_color = request_data.get("hair_color", people.hair_color)
    people.skin_color = request_data.get("skin_color", people.skin_color)
    people.eye_color = request_data.get("eye_color",  people.eye_color)
    people.birth_day = request_data.get("birth_day", people.birth_day)
    people.gender = request_data.get("gender", people.gender)
    people.species = request_data.get("species", people.species)
    people.home_planet = request_data.get("home_planet", people.home_planet)

    db.session.commit()
    return jsonify({"mensaje": "Personaje actualizado"}), 200

# DELETE Planet - People
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):

    planet = Planet.query.get(planet_id)

    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({"mensaje": "Planeta borrado"}), 200

@app.route('/peoples/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):

    people = People.query.get(people_id)

    if not people:
        return jsonify({"error": "Personaje no encontrado"}), 404

    db.session.delete(people)
    db.session.commit()

    return jsonify({"mensaje": "Personaje borrado"}), 200

