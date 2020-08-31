from datetime import timedelta
from flask import current_app as app

import redis


def get_redix_prefix_jwt_token():
    return app.config["REDIS_PREFIX_JWT_TOKEN"] + ":"


def connect_with_redis():
    return redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=0,
        decode_responses=True,
    )


class RedisModel(object):
    @classmethod
    def latest_instance_id_key(cls):
        """
        'key' to track id of latest instance of model 'demo'. Redis has no counter therefore we need to track id for
        own self.
        """
        pass

    @classmethod
    def list_key(cls):
        """
        'key' for the list which will contain 'ids' of all model instances

        Example:
        Consider model 'demo', this method will return 'demos'
        """
        pass

    def add_to_list(self):
        """
        Consider model 'demo', this method will add 'demo.id' to 'demos'
        """
        pass

    @classmethod
    def latest_instance_id(cls):
        """
        This will use 'latest_instance_id_key' and will return the value stored at this key.
        latest_instance-id will give the value of latest_instance_id_keys.
        """
        pass

    def increment_latest_instance_id(self):
        """
        Once an instance is added to redis, increase counter by 1.
        """
        pass

    @classmethod
    def cache_key(cls):
        """
        This generates a 'key' for a new instance being added.

        Example:
        Consider model 'demo'. if 5 instances of demo are already in Redis and a new instance is being added, then this
        would return 'demo-6'.
        """
        pass

    def save(self):
        """
        This inserts a new instance to redis.
        """
        pass

    def set_logout_key(self, token_jti, token_name):
        app.logger.info(
            f"entered: set logout key with token: {token_jti} and token_name: {token_name}"
        )
        connection = connect_with_redis()
        app.logger.info(connection)
        if token_name == "access":
            connection.set(
                token_jti,
                1,
                timedelta(
                    minutes=app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"]
                ),
            )
        elif token_name == "refresh":
            connection.set(
                token_jti,
                1,
                timedelta(
                    minutes=app.config["JWT_REFRESH_TOKEN_EXPIRES_MINUTES"]
                ),
            )
        app.logger.info("exit: set logout key")
