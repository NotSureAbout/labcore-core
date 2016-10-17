from flask import Blueprint, request, render_template, jsonify, url_for, redirect, g, json
from .models import User
from . import app, db
from sqlalchemy.exc import IntegrityError
from .utils.auth import generate_token, requires_auth, verify_token
import uuid


main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')


@main.route("/api/user", methods=["GET"])
@requires_auth
def get_user():
    return jsonify(result=g.current_user)


@main.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    user = User(
        id=str(uuid.uuid4()),
        email=incoming["email"],
        password=incoming["password"]
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409

    new_user = db.session.query(User).filter_by(id=user.id).first()

    print(new_user)

    return jsonify(
        id=user.id,
        token=generate_token(new_user)
    )


@main.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = User.get_user_with_email_and_password(incoming["email"],
                                                 incoming["password"])
    if user:
        return jsonify(token=generate_token(user))

    return jsonify(error=True), 403


@main.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403
