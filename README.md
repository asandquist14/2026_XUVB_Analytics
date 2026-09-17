# Xavier Women's Volleyball Analytics (IN PROGRESS)

A Python and Streamlit application for recording and analyzing Xavier Women's Volleyball practice and match statistics.

## Overview

This project was created to make volleyball statistics easier to record during practices and games and to turn those entries into useful reports for the coaching staff.

The application stores individual events in a SQLite database and provides live statistics for attacking, serving, and serve receive.

## Features

### Attack
- Record kills, errors, and attempts
- Track the attacker and setter
- Separate attacks by:
  - Outside
  - Right Side
  - Middle
- Track left-court and right-court attack locations
- Track rotations
- View statistics overall, by rotation, by player, by attack side, by setter, or by setter and attack side
- Undo the most recent entry
- Clear the current practice's attack data

### Serving
- Record serve ratings from 0–4
- Track aces, errors, total serves, and average serve rating
- Break serving statistics down by rotation or player

### Serve Receive
- Record pass ratings from 0–3
- Track perfect passes, good passes, poor passes, errors, and average rating
- Break passing statistics down by rotation or player

### Reports
The Reports Dashboard combines the different statistical areas into one view.

It includes:
- Attack %
- Kill %
- Serve average
- Pass average
- Master practice report
- Individual player dashboards
- Attack breakdowns by setter, attack side, and rotation
- Practice trends over time

## Technology

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenPyXL

## Project Structure

```text
2026_XUVB_Analytics/
├── app.py
├── config.py
├── setup_database.py
├── requirements.txt
├── data/
│   ├── roster.csv
│   ├── volleyball.db
│   └── exports/
├── database/
│   ├── database.py
│   └── queries.py
├── pages/
│   ├── attack.py
│   ├── recieve.py
│   ├── reports.py
│   └── serving.py
├── utils/
│   ├── roster.py
│   ├── session.py
│   └── utils.py
└── reports/
```

## Running the Application

Install the required packages:

```bash
pip install -r requirements.txt
```

Initialize the database:

```bash
python setup_database.py
```

Start the Streamlit application:

```bash
streamlit run app.py
```

## Data Structure

The SQLite database contains separate tables for:

- `attacks`
- `serves`
- `serve_receive`
- `matches`

Each entry is connected to a practice date and, where applicable, a drill, player, rotation, or match.

## Statistical Calculations

For attacks:

**Attack %**

```text
(Kills - Errors) / Total Attempts
```

**Kill %**

```text
Kills / Total Attempts
```

Serve statistics use a 0–4 rating scale, while serve receive uses a 0–3 rating scale.

## Notes

This project is designed around the needs of a volleyball coaching staff and is intended to be developed alongside the team's changing analytics needs. The application is currently focused on practice and match-level data collection rather than long-term predictive modeling.

Because the repository can contain team data, roster information, and game/practice records, sensitive or non-public volleyball data should not be committed to a public repository.
