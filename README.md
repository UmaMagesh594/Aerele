# Inventory Management (Flask)

Simple Flask app for tracking products across locations with movement logs and a balance report.

## Run

1. Create virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
    2. Run the app:
    • export FLASK_APP=app.py
flask run
    3. Visit http://127.0.0.1:5000/
Notes
    • Uses SQLite for demo. To use MySQL, change SQLALCHEMY_DATABASE_URI in app.py.
    • Add seed data by creating Products and Locations, then add Movements. ```
