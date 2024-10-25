from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields,validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:a3$pa202O.@localhost/workout"
ma = Marshmallow(app)
db = SQLAlchemy(app)


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    workouts = db.relationship('Workout', backref='member')

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    class Meta:
        fields = ('id', 'name', 'email', 'workouts')

class WorkoutSchema(ma.Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    class Meta:
        fields = ('id', 'name', 'description', 'member_id')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(name=member_data['name'], email=member_data['email'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added"}), 201

@app.route('/members', methods=['GET'])
def get_member():
    members = Member.query.all()
    return member_schema.jsonify(members)

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = Workout.query.get(id)
    if workout:
        return workout_schema.jsonify(workout)
    else:
        return jsonify({"error": "Workout not found"}), 404

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['name']
    member.email = member_data['email']
    db.session.commit()
    return jsonify({"message": "Member updated"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted"}), 200

@app.route('/workouts', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_workout = Workout(name=workout_data['name'], description=workout_data['description'], member_id=workout_data['member_id'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "New workout added"}), 201

@app.route('/members/<int:id>/workouts', methods=['GET'])
def get_member_workouts(id):
    member = Member.query.get_or_404(id)
    return workouts_schema.jsonify(member.workouts)

@app.route('/workouts/<int:id>/workouts', methods=['PUT'])
def update_workout(id):
    workout = Workout.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout.name = workout_data['name']
    workout.description = workout_data['description']
    db.session.commit()
    return jsonify({"message": "Workout updated"}), 200

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return workouts_schema.jsonify(workouts)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

