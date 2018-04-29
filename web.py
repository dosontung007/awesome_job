from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = 'jobs.db'


def load_db():

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db.cursor()


def query_db(query, args=(), one=False):
    cur = load_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else ()) if one else rv


@app.route('/')
def render():
    query = 'select id, title from jobs;'
    id_n_title = query_db(query)
    return render_template('index.html', id_n_title=id_n_title)


@app.route('/<id>')
def render_job(id):
    query = 'select title, description from jobs where id = ?'
    title, description = query_db(query, (id,), True)
    return render_template('job.html', title=title, description=description)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
