from sqlalchemy.orm.exc import NoResultFound

from models.redis_models.redis_model import (
    get_redix_prefix_jwt_token,
    connect_with_redis,
    RedisModel,
)


def add_token_to_database(encoded_token, identity_claim):
    pass


def is_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token["jti"]
    try:
        jti = get_redix_prefix_jwt_token() + jti
        if connect_with_redis().exists(jti):
            return True
    except NoResultFound:
        return True
    return False


def revoke_token(token_jti, token_name):
    """Revokes the given token

    Since we use it only on logout that already require a valid access token,
    if token is not found we raise an exception
    """
    try:
        jti = get_redix_prefix_jwt_token() + token_jti
        RedisModel().set_logout_key(token_jti=jti, token_name=token_name)
    except NoResultFound:
        raise Exception("Could not find the token {}".format(token_jti))
