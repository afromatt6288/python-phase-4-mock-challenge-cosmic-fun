from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serialize_rules = ('-scientist.missions', '-planet.missions',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Missions must have a name")
        return name

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        scientists = Scientist.query.all()
        ids = [scientist.id for scientist in scientists]
        if not scientist_id:
            raise ValueError("Missions must have a scientist_id")
        elif scientist_id not in ids:
            raise ValueError('Scientist must exist.')
        # elif any(mission for mission in Mission.query.filter_by(scientist_id=scientist_id)):
        #     raise ValueError("Scientist cannot accept the same mission twice")
        return scientist_id
    
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        planets = Planet.query.all()
        ids = [planet.id for planet in planets]
        if not planet_id:
            raise ValueError("Missions must have a planet_id")
        elif not planet_id in ids:
            raise ValueError('planet must exist.')
        return planet_id

    def __repr__(self):
        return f'<Mission: {self.name}, Scientist: {self.scientist.name}, Planet: {self.planet.name}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_rules = ('-missions.scientist',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

## cascade is added to allow the deletion of a scientist to also delete the Mission they are associated with ##
    missions = db.relationship('Mission', backref='scientist', cascade="all, delete, delete-orphan")
## This was in the solution code, but I do not know what it is or means... ##
    # planets = association_proxy('missions', 'planet')

    def __repr__(self):
        return f'<Scientist: {self.name}, Field of Study: {self.field_of_study}, Avatar: {self.avatar}>'
  
    @validates('name')
    def validate_name(self, key, name):
        scientists = Scientist.query.all()
        names = [scientist.name for scientist in scientists]
        if not name:
            raise ValueError("Scientists must have a name")
        elif name in names:
            raise ValueError("Name must be unique")
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if not field_of_study:
            raise ValueError("Scientists must have a field_of_study")
        return field_of_study
    
class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_rules = ('-missions.planet',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

## cascade is added to allow the deletion of a Planet to also delete the Mission it is associated with ##
    missions = db.relationship('Mission', backref='planet', cascade="all, delete, delete-orphan")
## This was in the solution code, but I do not know what it is or means... ##
    # scientists = association_proxy('missions', 'scientist')
    
    def __repr__(self):
        return f'<Planet: {self.name}, Distance From Earth: {self.distance_from_earth}, Nearest Star: {self.nearest_star}>'