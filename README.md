# Football Vault

Football Vault is a personal project for collecting, organising, and exploring football data. It includes club details, match results, lineups, and more, gathered from various sources and structured for easy access and analysis.

## Features

- Comprehensive datasets: clubs, matches, lineups, stadiums, and more
- Organised by season and competition
- Scripts for importing, exporting, and updating data
- Simple frontend app for browsing and managing the data


## Data Storage

All core data is stored in a local SQLite database:

- `football-vault.db` — Main SQLite database containing all data
- `data/` — Core JSON datasets exported from the SQLite database

## Project Structure

- `admin/` — Frontend app (Flask) for viewing and managing data
- `lineups/` — Match lineups by season
- `matches/` — Match data by competition and season
- `scripts/` — Import/export scripts (Python, Node.js)
- `sql-scripts/` — SQL utilities for advanced data management

## Frontend App

The admin frontend is a Flask app for browsing and editing your football data.

### Running the Frontend

1. Install Python dependencies (Flask, etc.):
   ```
   pip install flask
   ```

2. Start the app:
   ```
   cd admin
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```
