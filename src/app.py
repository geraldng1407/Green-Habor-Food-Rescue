import socket
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'db_conn') + '/foodrescue'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                           'pool_recycle': 280}

db = SQLAlchemy(app)

CORS(app)

 
class FoodRescue(db.Model):
    __tablename__ = 'foodrescue'

    __tablename__ = 'foodrescue'

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    dateposted = db.Column(db.DateTime, nullable=False)
    datefrom = db.Column(db.DateTime, nullable=False)
    dateto = db.Column(db.DateTime, nullable=False)
    coordinate_long = db.Column(db.FLOAT, nullable=False)
    coordinate_lat = db.Column(db.FLOAT, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    foodtype = db.Column(db.String(64), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    def __init__(self, title, description, dateposted, datefrom,
                 dateto, coordinate_long, coordinate_lat, location,
                 foodtype, verified):
        self.title = title
        self.description = description
        self.dateposted = dateposted
        self.datefrom = datefrom
        self.dateto = dateto
        self.coordinate_long = coordinate_long
        self.coordinate_lat = coordinate_lat
        self.location = location
        self.foodtype = foodtype
        self.verified = verified

    def to_dict(self):
        return {
            'post_id': self.post_id,
            'title': self.title,
            'description': self.description,
            'dateposted': self.dateposted,
            'datefrom': self.datefrom,
            'dateto': self.dateto,
            'coordinate_long': self.coordinate_long,
            'coordinate_lat': self.coordinate_lat,
            'location': self.location,
            'foodtype': self.foodtype,
            'verified': self.verified
        }


@app.route("/health")
def health_check():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return jsonify(
        {
            "message": "Service is healthy.",
            "service:": "games",
            "ip_address": local_ip
        }
    ), 200


@app.route("/posts")
def get_all():
    posts = FoodRescue.query.all()

    if posts:
        return jsonify({
            "data": {
                "posts": [post.to_dict() for post in posts]
            }
        }), 200

    return jsonify({
        "message": "There are no posts."
    }), 404


@app.route("/posts/<int:post_id>")
def find_by_id(post_id):

    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()

    if post:
        return jsonify({
            "data": post.to_dict()
        }), 200

    return jsonify({
        "message": "Post not found."
    }), 404


@app.route("/posts", methods=['POST'])
def new_post():
    try:
        data = request.get_json()
        post = FoodRescue(**data)
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "message": "An error occurred creating the post.",
            "error": str(e)
        }), 500

    return jsonify({
        "data": post.to_dict()
    }), 201


@app.route("/posts/<int:post_id>", methods=['PUT'])
def replace_post(post_id):

    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()

    if post is None:
        return jsonify({
            "message": "Post not found."
        }), 404

    data = request.get_json()

    if all(key in data.keys() for
           key in ('title', 'description', 'dateposted', 'datefrom',
                   'dateto', 'coordinate_long', 'coordinate_lat', 'location',
                   'foodtype', 'verified')):
        post.title = data['title']
        post.description = data['description']
        post.dateposted = data['dateposted']
        post.datefrom = data['datefrom']
        post.dateto = data['dateto']
        post.coordinate_long = data['coordinate_long']
        post.coordinate_lat = data['coordinate_lat']
        post.location = data['location']
        post.foodtype = data['foodtype']
        post.verified = data['verified']

        try:
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred replacing the post.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": post.to_dict()
            }
        )
    return jsonify(
        {
            "message": "An error occurred replacing the post.",
            "error": "Keys are missing from the JSON object. " +
                     " Consider HTTP PATCH instead."
        }
    ), 500


@app.route("/posts/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    post = db.session.scalars(
        db.select(FoodRescue).
        with_for_update(of=FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()
    if post is None:
        return jsonify(
            {
                "data": {
                    "post_id": post_id
                },
                "message": "Post not found."
            }
        ), 404
    data = request.get_json()

    if 'title' in data.keys():
        post.title = data['title']
    if 'description' in data.keys():
        post.description = data['description']
    if 'dateposted' in data.keys():
        post.dateposted = data['dateposted']
    if 'datefrom' in data.keys():
        post.datefrom = data['datefrom']
    if 'dateto' in data.keys():
        post.dateto = data['dateto']
    if 'coordinate_long' in data.keys():
        post.coordinate_long = data['coordinate_long']
    if 'coordinate_lat' in data.keys():
        post.coordinate_lat = data['coordinate_lat']
    if 'location' in data.keys():
        post.location = data['location']
    if 'foodtype' in data.keys():
        post.foodtype = data['foodtype']
    if 'verified' in data.keys():
        post.verified = data['verified']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "message": "An error occurred updating the post.",
                "error": str(e)
            }
        ), 500
    return jsonify(
        {
            "data": post.to_dict()
        }
    )


@app.route("/posts/<int:post_id>", methods=['DELETE'])
def delete_game(post_id):
    post = db.session.scalars(
        db.select(FoodRescue).
        filter_by(post_id=post_id).
        limit(1)
    ).first()
    if post is not None:
        try:
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            return jsonify(
                {
                    "message": "An error occurred deleting the post.",
                    "error": str(e)
                }
            ), 500
        return jsonify(
            {
                "data": {
                    "post_id": post_id
                }
            }
        ), 200
    return jsonify(
        {
            "data": {
                "post_id": post_id
            },
            "message": "Post not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
