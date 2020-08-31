from flask.views import MethodView

from app import name_space


@name_space.route("/")
class UserAPI(MethodView):
    
    def get(self):
        return {"status": "Got new data"}
    
    def post(self):
        return {"status": "posted new data"}
    
    # def post(self):
    #     """
    #     Create a new user
    #     ---
    #     tags:
    #       - users
    #     definitions:
    #       - schema:
    #           id: Group
    #           properties:
    #             name:
    #              type: string
    #              description: the group's name
    #     parameters:
    #       - in: body
    #         name: body
    #         schema:
    #           id: User
    #           required:
    #             - email
    #             - name
    #           properties:
    #             email:
    #               type: string
    #               description: email for user
    #             name:
    #               type: string
    #               description: name for user
    #             address:
    #               description: address for user
    #               schema:
    #                 id: Address
    #                 properties:
    #                   street:
    #                     type: string
    #                   state:
    #                     type: string
    #                   country:
    #                     type: string
    #                   postalcode:
    #                     type: string
    #             groups:
    #               type: array
    #               description: list of groups
    #               items:
    #                 $ref: "#/definitions/Group"
    #     responses:
    #       201:
    #         description: User created
    #     """
    #     return {}
