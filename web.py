from math import ceil
import sqlite3

from flask import (Flask, render_template, g, redirect, abort,
                   url_for, abort)

app = Flask(__name__)
DATABASE = 'jobs.db'
PER_PAGE = 20


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


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


def count_jobs():
    query = 'select * from jobs'
    return len(query_db(query))


def get_jobs_for_page(page, PER_PAGE, count):
    query = 'select id, title from jobs limit ?, ?'
    start = (page - 1) * PER_PAGE

    if start + PER_PAGE + 1 > count:
        jobs_value = count - start
    else:
        jobs_value = PER_PAGE
    return query_db(query, (start, jobs_value))


@app.route('/', defaults={'page': 1})
@app.route('/page', defaults={'page': 1})
@app.route('/page/<int:page>')
def show_jobs(page):
    id_n_title = get_jobs_for_page(page, PER_PAGE, count)
    if not id_n_title:
        abort(404)
    return render_template('index.html', id_n_title=id_n_title, page=page, max_page= count // PER_PAGE + 1)


@app.route('/<id_>')
def render_job(id_):
    query = 'select title, description from jobs where id = ?'
    try:
        title, description = query_db(query, (id_,), True)
    except ValueError:
        title, description = ('', '')
    return render_template('job.html', title=title, description=description)


if __name__ == '__main__':
    with app.app_context():
        count = count_jobs()
    app.run(host="0.0.0.0", debug=True)
