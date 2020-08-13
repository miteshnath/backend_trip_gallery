import jwt
import time
import json
from datetime import datetime

from flask import Blueprint, jsonify, g
from flask import request
from flask_cors import cross_origin
from flask import current_app as _app
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim

from app import db
from app.models import Trip, User, Photo, Location
from app.utility.decorators import (
    validate_json, required_params, login_required)
from app.utility.image_upload import upload_to_s3


trip_bp = Blueprint('trip', __name__)


@trip_bp.route('/trips', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@login_required
@validate_json
@required_params('name', 'locations', 'start_date', 'end_date')
def add_trip():
    """
    add a new user trip
    """
    data = request.get_json()
    try:
        # add new trip
        new_trip = Trip(name=data['name'], user_id=g.user.id, start_date=datetime.strptime(
            data['start_date'], '%Y-%m-%d'), end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'))
        db.session.add(new_trip)
        db.session.commit()

        geolocator = Nominatim(user_agent=_app.name)
        for loc in data['locations']:
            _loc = geolocator.geocode(loc)
            new_loc = Location(name=loc, lat=_loc.latitude,
                               lng=_loc.longitude, trip_id=new_trip.id)
            db.session.add(new_loc)
            db.session.commit()
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error": "something unexpected occurred!"}), 400
    return jsonify({
        'data': "Trip added successfully."
    }), 201


@trip_bp.route('/trips', methods=['GET'])
@login_required
def fetch_user_trips():
    user_id = g.user.id
    trips = Trip.query.filter(Trip.user_id == user_id).all()
    res = []
    for trip in trips:
        res.append(json.loads(fetch_trip_details(trip.id)[
                   0].response[0].decode('utf-8'))["data"])
    return jsonify({"trips": res}), 200


@trip_bp.route('/trips/<id>', methods=['GET'])
@login_required
def fetch_trip_details(id):
    """
    fetch trip details
    """
    trip = Trip.query.filter(Trip.id == id).first()
    trip_json = trip._to_dict()
    trip_json["locations"] = []
    trip_json["photos"] = []
    trip_json["total_locations"] = trip.locations.count()
    trip_json["total_photos"] = trip.photos.count()
    for loc in trip.locations.all():
        trip_json["locations"].append(loc._to_dict())

    for photo in trip.photos.all():
        trip_json["photos"].append(photo._to_dict())

    return jsonify({
        'data': trip_json
    }), 200


@trip_bp.route('/trips/<id>', methods=['PATCH'])
@login_required
@validate_json
def update_trip_details(id):
    """
    fetch trip details
    """
    trip = Trip.query.filter(Trip.id == g.user.id).first()
    payload = request.get_json()
    geolocator = Nominatim(user_agent=_app.name)
    if 'locations' in payload.keys():
        _loc = payload['locations']
        _loc = geolocator.geocode(_loc)
        new_loc = Location(name=payload['locations'], lat=_loc.latitude,
                           lng=_loc.longitude, trip_id=trip.id)
        db.session.add(new_loc)
        db.session.commit()

    return jsonify({
        'message': 'trip updated successfully.' 
    }), 200


@trip_bp.route('/trips/<trip_id>/photos', methods=['GET'])
@login_required
def fetch_trip_photos(trip_id):
    """
    fetch trip photos
    """
    trip = Trip.query.filter(Trip.id == trip_id).first()
    trip_photos = []

    for photo in trip.photos.all():
        trip_photos.append(photo._to_dict())

    return jsonify({
        'data': trip_photos
    }), 200


@trip_bp.route('/trips/<trip_id>/locations', methods=['GET'])
@login_required
def fetch_trip_locations(trip_id):
    """
    fetch trip locations
    """
    trip = Trip.query.filter(Trip.id == trip_id).first()
    trip_locations = []

    for loc in trip.locations:
        trip_locations.append(loc._to_dict())

    return jsonify({
        'data': trip_locations
    }), 200


@trip_bp.route('/trips/<trip_id>/photos', methods=['POST'])
@login_required
def post_trip_photos(trip_id):
    """
    post trip photos
    """
    content_type = request.mimetype
    image_files = request.files.getlist("file")

    trip = Trip.query.filter(Trip.id == trip_id).first()
    if not trip:
        return jsonify({"error": "trip_id is invalid!"})

    for image in image_files:
        url = upload_to_s3(g.user, content_type, image)
        try:
            _new_pic = Photo(image=url, trip_id=trip.id)
            db.session.add(_new_pic)
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return jsonify({"error": "oops! something unexpected happened."})

    return jsonify({"message": "images uploaded successfully."})
