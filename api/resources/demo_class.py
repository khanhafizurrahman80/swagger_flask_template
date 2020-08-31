from flask import jsonify
from flask_restful import Resource


class DemoResource(Resource):
    """Creation and get_all

        ---
        get:
          tags:
            - demo
          responses:
            200:
              content:
                application/json:
                  schema:
                    allOf:
                      - $ref: '#/components/schemas/PaginatedResult'
                      - type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/UserSchema'
        post:
          tags:
            - demo
          requestBody:
            content:
              application/json:
                schema:
                  DemoSchema
          responses:
            201:
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      msg:
                        type: string
                        example: user created
                      user: DemoSchema
        """
    
    def get(self):
        return 'hi', 200
    
    def post(self):
        pass
