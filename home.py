from db import get_db
import functools
import cv2
import serial

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

serialPort = serial.Serial(port = "COM7", baudrate=115200)
serialPort.flushInput()

bp = Blueprint('home', __name__, url_prefix='/home')

button = "stop"
IndividualMotor = [0, 0, 0, 0]
SendSlaveMotor = ""
SpeedMotor = 50

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

    if button == 'upleft':
        IndividualMotor = [0, SpeedMotor, -SpeedMotor, 0]
    elif button == "up":
        IndividualMotor = [SpeedMotor, SpeedMotor, -SpeedMotor, -SpeedMotor]
    elif button == "upright":
        IndividualMotor = [SpeedMotor, 0, 0, -SpeedMotor]
    elif button == "turnleft":
        IndividualMotor = [SpeedMotor, SpeedMotor, SpeedMotor, SpeedMotor]
    elif button == "left":
        IndividualMotor = [-SpeedMotor, SpeedMotor, -SpeedMotor, SpeedMotor]
    elif button == "right":
        IndividualMotor = [SpeedMotor, -SpeedMotor, SpeedMotor, -SpeedMotor]
    elif button == "turnrigt":
        IndividualMotor = [-SpeedMotor, -SpeedMotor, -SpeedMotor, -SpeedMotor]
    elif button == "downleft":
        IndividualMotor = [-SpeedMotor, 0, 0, SpeedMotor]
    elif button == "down":
        IndividualMotor = [-SpeedMotor, -SpeedMotor, SpeedMotor, SpeedMotor]
    elif button == "downright":
        IndividualMotor = [0, -SpeedMotor, SpeedMotor, 0]
    else:
        IndividualMotor = [0, 0, 0, 0]
    
    SendSlaveMotor = f"*{IndividualMotor[0]},{IndividualMotor[1]},{IndividualMotor[2]},{IndividualMotor[3]}#"
    serialPort.write(SendSlaveMotor)


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
