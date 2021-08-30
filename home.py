import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from db import get_db

bp = Blueprint('home', __name__, url_prefix='/home')


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        # get input button
        input = list(request.form.to_dict().keys())
        button, _ = input[0].split('-')
        print(button + ' pressed')
        # update database
        dbHandler = get_db()
        if (button == 'stop'):
            dbHandler.execute(
                'UPDATE movement SET act = 0'
            )
        else:
            dbHandler.execute(
                'UPDATE movement SET act = ? WHERE move_name = ?',
                (1, button)
            )
        dbHandler.commit()

    return render_template('home.html')
