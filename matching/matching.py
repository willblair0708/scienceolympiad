from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mentors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mentor and Student models
class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    interests = db.Column(db.String(100))
    availability = db.Column(db.String(50))
    location = db.Column(db.String(50))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    interests = db.Column(db.String(100))
    availability = db.Column(db.String(50))
    location = db.Column(db.String(50))

# Mentor-Student matching algorithm
def match_mentors_students(mentors, students):
    matches = []
    for mentor in mentors:
        for student in students:
            if mentor.interests == student.interests and mentor.availability == student.availability and mentor.location == student.location:
                matches.append((mentor, student))
    return matches

# Routes for creating mentors and students
@app.route('/mentors', methods=['POST'])
def create_mentor():
    data = request.get_json()
    new_mentor = Mentor(name=data['name'], email=data['email'], interests=data['interests'], availability=data['availability'], location=data['location'])
    db.session.add(new_mentor)
    db.session.commit()
    return jsonify({'message': 'Mentor created successfully!'})

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    new_student = Student(name=data['name'], email=data['email'], interests=data['interests'], availability=data['availability'], location=data['location'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student created successfully!'})

# Route for matching mentors and students
@app.route('/matches', methods=['GET'])
def get_matches():
    mentors = Mentor.query.all()
    students = Student.query.all()
    matches = match_mentors_students(mentors, students)
    return jsonify({'matches': matches})

if __name__ == '__main__':
    app.run(debug=True)
