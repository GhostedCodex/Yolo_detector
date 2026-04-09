from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="../templates",
                static_folder="../static")
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max

    from .routes import bp
    app.register_blueprint(bp)
    return app
