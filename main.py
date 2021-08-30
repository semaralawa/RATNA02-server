import os

from flask import Flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load database
    import db
    db.init_app(app)
    # if there's no database, create one
    if(os.path.exists(os.path.join(app.instance_path, 'flaskr.sqlite')) == False):
        with app.app_context():
            db.init_db()
            # add preset movement data
            dbHandler = db.get_db()
            preset_movement = ('upleft', 'up', 'upright', 'turnleft', 'left',
                               'right', 'turnright', 'downleft', 'down', 'downright')
            for move in preset_movement:
                dbHandler.execute(
                    'INSERT INTO movement (move_name, act) VALUES (?, ?)',
                    (move, 0)
                )
            dbHandler.commit()

    import auth
    app.register_blueprint(auth.bp)

    import home
    app.register_blueprint(home.bp)

    # redirect page to login page
    @app.route('/')
    def hello():
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True, host='0.0.0.0', use_reloader=True)
