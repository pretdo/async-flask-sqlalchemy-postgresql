#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from gevent.monkey import patch_all
patch_all()
from psycogreen.gevent import patch_psycopg
patch_psycopg()



app = Flask(__name__)
app.config.from_pyfile('config.py')


db = SQLAlchemy(app)
db.engine.pool._use_threadlocal = True


class Todo(db.Model):

    """ Small example model just to show you that SQLAlchemy is
        doing everything it should be doing.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    done = db.Column(db.Boolean)
    priority = db.Column(db.Integer)

    def as_dict(self):
        """ Return an individual Todo as a dictionary.
        """
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done,
            'priority': self.priority
        }

    @classmethod
    def jsonify_all(cls):
        """ Returns all Todo instances in a JSON
            Flask response.
        """
        return jsonify(todos=[todo.as_dict() for todo in cls.query.all()])


@app.route('/sleep/postgres/')
def sleep_postgres():
    """ This handler asks Postgres to sleep for 5s and will
        block for 5s unless psycopg2 is set up (above) to be
        gevent-friendly.
    """
    db.session.execute('SELECT pg_sleep(5)')
    return Todo.jsonify_all()


def create_data():
    """ A helper function to create our tables and some Todo objects.
    """
    db.create_all()
    todos = []
    for i in range(50):
        todo = Todo(
            title="Slave for the man {0}".format(i),
            done=(i % 2 == 0),
            priority=(i % 5)
        )
        todos.append(todo)
    db.session.add_all(todos)
    db.session.commit()


if __name__ == '__main__':

    if '-c' in sys.argv:
        create_data()
    else:
        app.run()
