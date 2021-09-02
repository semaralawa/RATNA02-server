import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

import cv2

from db import get_db

bp = Blueprint('home', __name__, url_prefix='/home')
camera = cv2.VideoCapture(0)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@bp.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    if request.method == 'POST':
        # get input button
        input = list(request.form.to_dict().keys())
        button, _ = input[0].split('-')
        print(button + ' pressed')
        # update database
        dbHandler = get_db()
        # reset it first
        dbHandler.execute(
            'UPDATE movement SET act = 0'
        )
        dbHandler.commit()
        if (button != 'stop'):
            dbHandler.execute(
                'UPDATE movement SET act = ? WHERE move_name = ?',
                (1, button)
            )
            dbHandler.commit()

    return render_template('home.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id
