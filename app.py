import os
import time
import redis
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)
cache = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)

def get_db_connection():
    conn = psycopg2.connect(
            host=os.environ.get('DATABASE_HOST', 'localhost'),
            database=os.environ.get('POSTGRES_DB', 'mydatabase'),
            user=os.environ.get('POSTGRES_USER', 'myuser'),
            password=os.environ.get('POSTGRES_PASSWORD', 'mypassword')
    )
    return conn

def get_hit_count():
    retries = 5
    while True:
        try:
            # Increment a counter in Redis
            count = cache.incr('hits')
            return count
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    try:
        count = get_hit_count()
        return f'Hello from Flask! I have been seen {count} times.\n'
    except Exception as e:
        return f'Hello from Flask! Could not connect to Redis. Error: {e}\n'

@app.route('/db')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Create a simple table if it doesn't exist
        cur.execute("CREATE TABLE IF NOT EXISTS visits (count INT)")
        # Increment a simple counter in the database (simplistic for demo)
        cur.execute("INSERT INTO visits (count) VALUES (1)")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM visits")
        db_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f'Hello from Flask! Database visits: {db_count}\n'
    except Exception as e:
        return f'Hello from Flask! Could not connect to database. Error: {e}\n'

if __name__ == "__main__":
    # In production, use a WSGI server like Gunicorn or uWSGI
    app.run(host="0.0.0.0", debug=True)
