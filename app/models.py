from app import db


class BaseModel(db.Model):
    """
    Base data model for all objects
    """
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """
        base way to print models
        """
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def _to_dict(self):
        """
        base way to jsonify models, dealing with datetime objects
        """
        as_json = {
            column: value for column, value in self.__dict__.items()
        }
        del as_json['_sa_instance_state']
        return as_json


class User(BaseModel, db.Model):
    """
    Model for the users table
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    jwt = db.Column(db.String(300), nullable=True)
    trips = db.relationship('Trip', backref='users', lazy=True)
    dp = db.Column(db.String(
        120), default="https://ethos-photos.s3.ap-south-1.amazonaws.com/default_dp.png")


class Trip(BaseModel, db.Model):
    """
    Model for user trips
    """
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    photos = db.relationship('Photo', backref='photos', lazy="dynamic")
    locations = db.relationship(
        'Location', backref='locations', lazy="dynamic")


class Photo(BaseModel, db.Model):
    """
    Model to store trip pics
    """
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(120), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)


class Location(BaseModel, db.Model):
    """
    Model for user trip locations
    """
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
