from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from api.resources.demo_class import DemoResource
from api.schemas import DemoSchema
from extension import apispec

blueprint = Blueprint("api", __name__, url_prefix='/api/v1')
api = Api(blueprint)

api.add_resource(DemoResource, "/demos", endpoint="demos")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("DemoSchema", schema=DemoSchema)
    apispec.spec.path(view=DemoResource, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

       This will avoid having to try/catch ValidationErrors in all endpoints, returning
       correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
       """
    return jsonify(e.messages), 400
