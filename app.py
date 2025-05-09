from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for, flash, session



app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# ---------------------------
# ROUTES
# ---------------------------

# database configuration---------------------------------------
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/smartupcycle"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Defining model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Defining model class for the 'login' table
class login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


#Singup 
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(username=username, email=email, password=password)
        db.session.add(new_signup)
        db.session.commit()

        return send_from_directory('frontend', 'login.html')  # Redirect to login page after signup

    return send_from_directory('frontend', 'signup.html')  # Show signup form if GET request


@app.route('/login', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Signup.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            flash('Login successful!', 'success')
            return send_from_directory('frontend','index.html')
        else:
            flash('Invalid username or password', 'danger')
            return send_from_directory('frontend','login.html')

    return send_from_directory('frontend','login.html')


# Home page
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# DIY Suggestion Route
@app.route('/diy', methods=['POST'])
def diy_suggestions():
    if 'file' in request.files:
        image = request.files['file']
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
        return jsonify({'suggestion': 'Turn this item into a plant holder or storage box.'})

    data = request.json
    description = data.get('description', '')
    return jsonify({'suggestion': f'Based on "{description}", you could create a DIY organizer.'})

# Carbon Analyzer Route
@app.route('/carbon', methods=['POST'])
def analyze_carbon():
    data = request.json
    electricity = float(data.get('electricity', 0))
    meals = int(data.get('meals', 0))
    travel = float(data.get('travel', 0))

    co2_total = electricity * 0.85 + meals * 2.5 + travel * 0.21

    suggestions = [
        "Switch to LED bulbs",
        "Try plant-based meals twice a week",
        "Use public transport for short trips"
    ]

    return jsonify({
        'footprint_kg': round(co2_total, 2),
        'suggestions': suggestions
    })

# Marketplace upload handler
@app.route('/marketplace', methods=['POST'])
def post_diy_item():
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('file')

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

    return jsonify({'message': 'DIY item uploaded successfully!'})


@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(app.static_folder, filename)

# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
