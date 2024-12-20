from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

from teamlist import teamlist

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure, random key

# Path to the JSON file
DATA_FILE = 'scouting_data.json'
USERS = {
    "admin": "555"  # Replace "555" with your desired password
}

# Load existing data from JSON file or initialize an empty list
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as file:
        scouting_data = json.load(file)
else:
    scouting_data = []

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verify credentials
        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash("Successfully logged in!", "success")
            return redirect(url_for('admin'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for('login'))

    # Display login form
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Middleware to clear session on navigation
@app.before_request
def clear_session_on_navigation():
    # Allow access to static files and login/logout
    if request.endpoint and (request.endpoint.startswith('static') or request.endpoint in ['login', 'logout']):
        return

    # Clear the session when switching pages
    if 'username' in session and request.endpoint not in ['admin', 'login']:
        session.pop('username', None)

# Home route
@app.route('/')
def home():
    return render_template('home.html', teams=teamlist)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/scout')
def scout():
    return render_template('scout.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

# Admin route (protected)
@app.route('/admin')
def admin():
    if 'username' not in session:  # Check if user is logged in
        flash("You must be logged in to view the admin page.", "warning")
        return redirect(url_for('login'))

    return render_template('admin.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)


# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    team_number = request.form['team-number']
    match_number = request.form['match-number']
    performance = request.form['performance']
    score = int(request.form['score'])

    # Find the existing team or add a new one
    team_data = next((team for team in scouting_data if team['team_number'] == team_number), None)
    if not team_data:
        team_data = {
            'team_number': team_number,
            'matches': []
        }
        scouting_data.append(team_data)

    # Add the match result to the team
    team_data['matches'].append({
        'match_number': match_number,
        'performance': performance,
        'score': score
    })

    # Save the updated scouting data back to the JSON file
    with open(DATA_FILE, 'w') as file:
        json.dump(scouting_data, file, indent=4)

    return redirect(url_for('home'))

# Display team results
@app.route('/team/<team_number>')
def team_results(team_number):
    # Find the team's data from the scouting_data.json file
    team_data = next((team for team in scouting_data if team['team_number'] == team_number), None)
    if not team_data:
        team_data = {
            'team_number': team_number,
            'matches': []
        }
    return render_template('team_results.html', team=team_data)

if __name__ == "__main__":
    app.run(debug=True)
