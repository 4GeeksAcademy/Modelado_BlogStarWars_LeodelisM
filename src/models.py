from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    date_suscripcion:  Mapped[int] = mapped_column(DateTime(), nullable=False) 
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "date_suscripcion": self.date_suscripcion.isoformat(),
            "is_active": self.is_active
        }

    # Relaciones 
    user_fav = relationship("favorite", back_populates="user")

class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_people: Mapped[str] = mapped_column(String(250), nullable=False)
    height: Mapped[float] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    hair_color: Mapped[str] = mapped_column(String(100), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(100), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_day: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(100), nullable=False)
    species:  Mapped[str] = mapped_column(String(100), nullable=False)
    home_planet:  Mapped[str] = mapped_column(String(100), nullable=False)

    def serialize(self):
        return{
            "id": self.id,
            "name_people": self.name_people,
            "height": self.height,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_day": self.birth_day,
            "gender": self.gender,
            "species": self.species,
            "home_planet": self.home_planet
        }

    # Relaciones
    character_fav= relationship("favorite", back_populates= "character")

class Planet(db.Model):
    __tablename__ = 'planet'

    id: Mapped[int] = mapped_column(primary_key=True)
    planet_name: Mapped[str] = mapped_column(String(100), nullable=False)
    diameter: Mapped[float] = mapped_column(nullable=False)
    climate: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)
    gravity: Mapped[float] = mapped_column(nullable=False)
    rotation_period: Mapped[float] = mapped_column(nullable=False)
    orbital_period: Mapped[float] = mapped_column(nullable=False)
    terrain: Mapped[str] = mapped_column(String(100), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
            "diameter": self.diameter,
            "climate": self.climate,
            "population": self.population,
            "gravity": self.gravity,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "terrain": self.terrain
        }
    
    # Relaciones
    planet_fav= relationship("favorite", back_populates="planet")

class Favorite(db.Model):
    __tablename__ = 'favorite'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    people_id: Mapped[int] = mapped_column(db.ForeignKey('people.id'), nullable= True)
    planet_id: Mapped[int] = mapped_column(db.ForeignKey('planet.id'), nullable= True)

    def serialize(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id
        }

    

