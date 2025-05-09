from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# ---------------------------
# ROUTES
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diy', methods=['POST'])
def diy_suggestions():
    """
    Accepts an uploaded image or text description and returns a sample DIY suggestion.
    Later, this would call an AI model or recommendation API.
    """
    if 'file' in request.files:
        image = request.files['file']
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
        return jsonify({'suggestion': 'Turn this item into a plant holder or storage box.'})

    data = request.json
    description = data.get('description', '')
    return jsonify({'suggestion': f'Based on "{description}", you could create a DIY organizer.'})

@app.route('/carbon', methods=['POST'])
def analyze_carbon():
    """
    Receives electricity usage, food, and travel data,
    returns a basic carbon footprint estimate and reduction suggestions.
    """
    data = request.json
    electricity = float(data.get('electricity', 0))
    meals = int(data.get('meals', 0))
    travel = float(data.get('travel', 0))

    # Dummy calculation
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

@app.route('/marketplace', methods=['POST'])
def post_diy_item():
    """
    Handles form submissions for the DIY marketplace.
    """
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('file')

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

    return jsonify({'message': 'DIY item uploaded successfully!'})

# Static file serving (e.g., frontend HTML)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
