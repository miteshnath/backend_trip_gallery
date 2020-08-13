import jwt
from flask import Blueprint, jsonify, url_for
from flask import request, g
from flask import current_app as _app
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.security import generate_password_hash, check_password_hash


import time
from app import db
from app.models import User
from app.utility.image_upload import upload_to_s3
from app.utility.decorators import (validate_json, required_params, login_required)


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_json
@required_params('username', 'password')
def register_user():
    """
    register a new user 
    """
    data = request.get_json()
    data["password"] = generate_password_hash(data["password"])
    try:
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "username already exists!"}), 400
    return jsonify({
        'data': "SignUp Successful!"
    }), 201


@auth_bp.route('/login', methods=['POST'])
@validate_json
@required_params('username', 'password')
def login():
    """
    register a new user 
    """
    data = request.get_json()
    user = User.query.filter(User.username==data['username']).first()
    if not user:
        return jsonify({"error": "username not found!"}), 400
    if not check_password_hash(user.password, data['password']):
        return jsonify({"error": "password is wrong!"}), 400
    
    try:
        user.jwt = jwt.encode({'user_id': user.id, "username": user.username}, _app.secret_key, algorithm='HS256').decode('UTF-8')
        db.session.commit()
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error":"oops! this is unexpected. Plz try later or contanct us!"})
    return jsonify({
        'access_token': user.jwt
    }), 200


@auth_bp.route('/upload-profile-picture', methods=['PATCH'])
@login_required
def upload_profile_picture():
    content_type = request.mimetype
    image_file = request.files['file']
    url = upload_to_s3(g.user, content_type, image_file)
    try:
        user = User.query.filter(User.id==g.user.id).first()
        user.dp = url
        db.session.commit()
        return jsonify({"message": "profile picture updated successfully"}), 200
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error":"oops! something unexpected occured."}), 400


@auth_bp.route('/logout', methods=['PATCH'])
@login_required
def logout():
    token = request.headers.get("Authorization", "")
    user = User.query.filter(User.id==g.user.id).first()
    if user.jwt != token:
        return jsonify({"error": "invalid login!"})
    try:
        user.jwt = ""
        db.session.commit()
        return jsonify({"message": "logout successfully"})
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error": "oops! something unexpected occured"})


@auth_bp.route('/user-profile', methods=['GET'])
@login_required
def fetch_user_profile():
    user = User.query.filter(User.id==g.user.id).first()
    return jsonify({"data": user._to_dict()})


@auth_bp.route('/user-profile', methods=['POST'])
@login_required
@validate_json
def update_user_profile():
    user = User.query.filter(User.id == g.user.id).first()
    url = user.dp
    email = user.email
    if request.get_json()["dp"]:
        content_type = request.mimetype
        image_file = request.files['dp']
        url = upload_to_s3(g.user, content_type, image_file)

    if request.get_json()["email"] != g.user.email:
        email = request.get_json()["email"]

    try:
        user.dp = url
        user.email = email
        db.session.commit()
        return jsonify({"message": "updated user details",
         "data": User.query.filter(User.id == g.user.id).first()._to_dict()})
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error": "oops! something unexpected occured."}), 400

