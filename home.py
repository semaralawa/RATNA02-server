from db import get_db
import functools
import cv2

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

bp = Blueprint('home', __name__, url_prefix='/home')

button = "stop"


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


def movement():
    global button
    print(button + ' pressed')


def gen_frames():  # generate frame by frame from camera
    camera = cv2.VideoCapture(0)
    camera.set(3, 1280)
    camera.set(4, 720)
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("camera open failed, repeating.....")
            break
        else:
            # execute movement function
            movement()
            # send image to web
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
        # force the module to find global scope variable
        global button
        # get input button
        button = request.form["value"]
        return button + ' pressed'

    return render_template('home.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
