import datetime
from http import HTTPStatus

from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from sqlalchemy.exc import SQLAlchemyError

from auth.helpers import add_token_to_database, revoke_token, is_token_revoked
from common.response import Response
from extension import db, pwd_context, apispec, jwt
from models.user import User
from schema.user import UserSchema

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["POST"])
def login():
    """Authenticate user and return tokens

    ---
    post:
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: admin
                  required: true
                password:
                  type: string
                  example: admin
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
                  refresh_token:
                    type: string
                    example: myrefreshtoken
        400:
          description: bad request
      security: []
    """
    if not request.is_json:
        response_body = {"message": "Missing JSON in request"}
        return (
            Response(400).wrap(response_body=response_body),
            HTTPStatus.BAD_REQUEST,
        )

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        response_body = {"message": "Missing username or password"}
        return (
            Response(400).wrap(response_body=response_body),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            response_body = {"message": "User not found"}
            return (
                Response(401).wrap(response_body=response_body),
                HTTPStatus.UNAUTHORIZED,
            )

    except Exception as e:
        app.logger.error(str(e))
        db.session.rollback()
        response_body = {"message": f"error occurred{str(e)}"}
        return (
            Response(500).wrap(response_body=response_body),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    if user is None or not pwd_context.verify(password, user.password):
        response_body = {"message": "Unauthorized"}
        return (
            Response(401).wrap(response_body=response_body),
            HTTPStatus.UNAUTHORIZED,
        )

    ret = create_response_body(user)
    response_body = {"data": ret}
    return Response(200).wrap(response_body=response_body), HTTPStatus.OK


def create_response_body(user):

    app.logger.info("create response body with user {0}".format(user))
    jwt_data = create_jwt_data({}, user)
    access_token = create_access_token(
        identity=jwt_data,
        expires_delta=datetime.timedelta(
            minutes=app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"]
        ),
    )
    refresh_token = create_refresh_token(
        identity=jwt_data,
        expires_delta=datetime.timedelta(
            minutes=app.config["JWT_REFRESH_TOKEN_EXPIRES_MINUTES"]
        ),
    )
    ret = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
    }
    return ret


def create_jwt_data(jwt_data, user):
    jwt_data["id"] = user.id
    jwt_data["username"] = user.username
    return jwt_data


@blueprint.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    """Get an access token from a refresh token

    ---
    post:
      tags:
        - auth
      parameters:
        - in: header
          name: Authorization
          required: true
          description: valid refresh token
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
        400:
          description: bad request
        401:
          description: unauthorized
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {"access_token": access_token}
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    return Response(200).wrap(response_body=ret), HTTPStatus.OK


@blueprint.route("/revoke_access", methods=["DELETE"])
@jwt_required
def revoke_access_token():
    """Revoke an access token

    ---
    delete:
      tags:
        - auth
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: bad request
        401:
          description: unauthorized
    """
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, "access")
    return (
        Response(200).wrap(response_body={"message": "token revoked"}),
        HTTPStatus.OK,
    )


@blueprint.route("/revoke_refresh", methods=["DELETE"])
@jwt_refresh_token_required
def revoke_refresh_token():
    """Revoke a refresh token, used mainly for logout

    ---
    delete:
      tags:
        - auth
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: token revoked
        400:
          description: bad request
        401:
          description: unauthorized
    """
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, "refresh")
    return (
        Response(200).wrap(response_body={"message": "token revoked"}),
        HTTPStatus.OK,
    )


def validation_data_check(mandatory_fields, req_data):
    for key in req_data:
        if key not in mandatory_fields:
            raise ValueError(f"{key} can not be present")
    field_missing = list(set(mandatory_fields) - set(list(req_data.keys())))
    if len(field_missing) != 0:
        raise ValueError(f"mandatory fields are missing {field_missing}")


def check_new_password_confirm_password(new_password, confirm_password):
    if len(new_password) != len(confirm_password):
        raise ValueError("password does not match")
    if new_password != confirm_password:
        raise ValueError("password does not match")
    if new_password.__eq__(confirm_password) is not True:
        raise ValueError("password does not match")


def fetch_change_pass_req_body(req_data):
    return (
        req_data["user_id"],
        req_data["current_password"],
        req_data["new_password"],
        req_data["confirm_password"],
    )


def validation_authority(current_user):
    # need to implement logic to verify whether current user is authorized to change password
    return "authorized"


@blueprint.route("/change_password", methods=["PUT"])
@jwt_required
def change_password():
    """Change the current password

    ---
    put:
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                  required: true
                current_password:
                  type: string
                  required: true
                new_password:
                  type: string
                  required: true
                confirm_password:
                  type: string
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: int
                    example: 200
                  success:
                    type: dict
                    example: {message: password changes successfully}
                  error:
                    type: dict
                    example: {message: error occurred}
        400:
          description: bad request
    """
    app.logger.info("change password")

    if not request.is_json:
        response_body = {"message": "Missing JSON in request"}
        return Response(400).wrap(response_body), HTTPStatus.BAD_REQUEST

    _mandatory_fields = [
        "user_id",
        "current_password",
        "new_password",
        "confirm_password",
    ]
    req_data = request.json
    try:
        validation_data_check(_mandatory_fields, req_data)
        user_id, current_password, new_password, confirm_password = fetch_change_pass_req_body(
            req_data=request.json
        )

        user = User.query.filter_by(id=user_id).first()
        app.logger.info(
            f"password mismatch {pwd_context.verify(current_password, user.password)}"
        )
        if user is None or not pwd_context.verify(
            current_password, user.password
        ):
            response_body = {"message": "unauthorized"}
            return Response(401).wrap(response_body), HTTPStatus.UNAUTHORIZED

        check_new_password_confirm_password(new_password, confirm_password)
        app.logger.info(get_jwt_identity())
        update_data = {
            "password": pwd_context.hash(new_password)
            # "updated_by": get_jwt_identity().get("username"),
            # "updated_on": datetime.datetime.now().isoformat(),
        }
        obj = UserSchema().load(update_data, instance=user, partial=True)
        db.session.add(obj)
        db.session.commit()
        response_body = {"message": "password changed successfully"}
        return Response(200).wrap(response_body), HTTPStatus.OK

    except ValueError as e:
        response_body = {"message": e.args[0]}
        return Response(400).wrap(response_body), HTTPStatus.BAD_REQUEST

    except SQLAlchemyError as e:
        app.logger.error(f"error occured while returned {str(e)}")
        response_body = {"message": f"{str(e)}"}
        return (
            Response(500).wrap(response_body),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@blueprint.route("/reset_password", methods=["PUT"])
@jwt_required
def reset_password():
    """Change the current password

    ---
    put:
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  required: true
                password:
                  type: string
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: int
                    example: 200
                  success:
                    type: dict
                    example: {message: password changes successfully}
                  error:
                    type: dict
                    example: {message: error occurred}
        400:
          description: bad request
    """
    if not request.is_json:
        response_body = {"message": "Missing JSON in request"}
        return (
            Response(400).wrap(response_body=response_body),
            HTTPStatus.BAD_REQUEST,
        )
        # return jsonify({"msg": "Missing JSON in request"}), HTTPStatus.BAD_REQUEST

    _mandatory_fields = ["username", "password"]
    req_data = request.json

    try:
        validation_data_check(_mandatory_fields, req_data)
        authorized_user = validation_authority(
            get_jwt_identity().get("username")
        )
        if authorized_user == "authorized":
            username = req_data["username"]
            password = req_data["password"]
            current_time = datetime.datetime.now().isoformat()
            current_user = get_jwt_identity().get("username")
            user = User.query.filter_by(username=username).first()

            if user is None:
                response_body = {"message": "user is not present"}
                return (
                    Response(401).wrap(response_body),
                    HTTPStatus.UNAUTHORIZED,
                )

            update_data = {
                "password": pwd_context.hash(password),
                # "updated_by": current_user,
                # "updated_on": current_time,
            }
            obj = UserSchema().load(update_data, instance=user, partial=True)
            db.session.add(obj)
            db.session.commit()
            response_body = {"message": "password reset successfully"}
            return Response(200).wrap(response_body), HTTPStatus.OK
        elif authorized_user == "unauthorized":
            response_body = {"message": "unauthorized"}
            return (
                Response(401).wrap(response_body=response_body),
                HTTPStatus.UNAUTHORIZED,
            )
        else:
            response_body = {"message": authorized_user}
            return (
                Response(500).wrap(response_body=response_body),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    except ValueError as e:
        response_body = {"message": e.args[0]}
        return Response(400).wrap(response_body), HTTPStatus.BAD_REQUEST

    except SQLAlchemyError as e:
        app.logger.error(f"error occured while returned {str(e)}")
        response_body = {"message": f"{str(e)}"}
        return (
            Response(500).wrap(response_body),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.get(identity["id"])


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=login, app=app)
    apispec.spec.path(view=refresh, app=app)
    apispec.spec.path(view=revoke_access_token, app=app)
    apispec.spec.path(view=revoke_refresh_token, app=app)
    apispec.spec.path(view=change_password, app=app)
    apispec.spec.path(view=reset_password, app=app)
