from flask import Flask, jsonify
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from app.extensions import cache, db, limiter, ma


def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    from .customer import customer_bp
    from .inventory import inventory_bp
    from .mechanic import mechanic_bp
    from .service_ticket import service_ticket_bp

    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(service_ticket_bp, url_prefix="/service-tickets")

    # --- SWAGGER SETUP ---
    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag["info"]["version"] = "1.0"
        swag["info"]["title"] = "Auto Shop API"

        # UPDATE THESE FOR PRODUCTION
        swag["host"] = "your-app-name.onrender.com"
        swag["schemes"] = ["https"]

        swag["securityDefinitions"] = {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme.",
            }
        }
        return jsonify(swag)

    swaggerui_bp = get_swaggerui_blueprint(
        "/docs", "/spec", config={"app_name": "Auto Shop API"}
    )
    app.register_blueprint(swaggerui_bp, url_prefix="/docs")

    return app
