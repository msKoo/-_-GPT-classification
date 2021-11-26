from flask import request, make_response
from flask_restx import Resource, Namespace

from service.analysis_service import request_body

Analysis = Namespace('Analysis')

@Analysis.route('')
class TestClass(Resource):
    def get(self):
        #빈도수 기준 정렬
        keyword = request.args.get("keyword", default="생기한의원", type=str)
        print(keyword)
        result = request_body(keyword)
        return make_response(result, 200)

    def post(self):
        # test = request.json.get()
        response = request.json.get("keyword")

        print(response)
        #SERVICE에서 처리한 값을 Result로 넘겨줌
        # result = SortingByFrequency()

        return make_response('result', 200)
