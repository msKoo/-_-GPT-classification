from flask import request, make_response
from flask_restx import Resource, Namespace

from service.reputation_service import repu_main

Reputation = Namespace('reputation')

@Reputation.route('')
class TestClass(Resource):
    def post(self):
        text = request.json.get("text")

        result = repu_main(text)

        return make_response(result, 200)
