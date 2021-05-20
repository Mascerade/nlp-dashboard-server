import sqlite3
import os
from typing import Dict, Tuple, List
from flask import Flask, request
from flask_cors import cross_origin

DATABASE_PATH = 'databases/'

app = Flask(__name__)
DATABASE_COLUMNS = 'Epoch INTEGER, Batch INTEGER, Accuracy REAL, Loss REAL, RunningAccuracy REAL, RunningLoss REAL'

@app.route('/create_db', methods=['PUT'])
@cross_origin()
def create_database() -> Tuple[Dict, int]:
    '''
    Create a new database given the model's name
    '''
    try:
        model_name = request.json['model_name'].lower()
        
        # Open connection to databse
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))

        # Use a cursor to create the database
        cur = conn.cursor()
        cur.execute('''CREATE TABLE data ({})'''.format(DATABASE_COLUMNS))
        
        # Save changes and close connection
        conn.commit()
        conn.close()

        return {'success': True}, 201

    except sqlite3.OperationalError as e:
        print('Message: {}'.format(str(e)))
        print('Database most likely already exists.')
        
        # Return 409 state-conflict error
        return {'success': False}, 409

    except Exception as e:
        print('Type: {} Message: {}'.format(type(e).__name__, str(e)))
        return {'success': False}, 400

@app.route('/add_data', methods=['PUT'])
@cross_origin()
def add_data() -> Tuple[Dict, int]:
    '''
    Add rows of data from training to the database
    '''

    try:
        model_name = request.json['model_name'].lower()
        batch_stats: List[List[int, int, float, float, float, float]] = request.json['data']

        # Open connection to the database
        conn = sqlite3.connect('{}/{}.db'.format(DATABASE_PATH, model_name))
        cur = conn.cursor()
        
        # Insert the values into the database
        for batch_stat in batch_stats:
            cur.execute(''' INSERT into data values ({}, {}, {}, {}, {}, {}) '''.format(*batch_stat))
        
        # Save the changes
        conn.commit()
        cur.close()

        return {'success': True}, 201

    except Exception as e:
        print('Type: {} Message: {}'.format(type(e).__name__, str(e)))
        return {'success': False}, 400

if __name__ == '__main__':
    app.run('localhost', port=3000, debug=True)