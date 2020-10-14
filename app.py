from flask import Flask, jsonify
from flask_restful import Api, Resource

import api
import auth
from extension import apispec, db, jwt


def configure_name(instance_name, app):

    from config import instances
    
    app.logger.info("configure_name {0}".format(instances[instance_name]))
    return instances[instance_name]


def configure_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    
    
def configure_apispec(app):
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app):
    """
    register all blueprints for application

    :param app: the instance of the application which need to be run
    :return: void

    """
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)


app = Flask("common")

app.config.from_object(configure_name('development', app))

configure_extensions(app)
configure_apispec(app)
register_blueprints(app)
app.app_context().push()
