from flask import request, make_response
from flask_restx import Resource, Namespace

from service.generator_service import request_body


Generator = Namespace('generator')

@Generator.route('')
class TestClass(Resource):
    def get(self):
        #빈도수 기준 정렬
        keyword = request.args.get("keyword", default="생기한의원", type=str)
        type = request.args.get("type", type=str)
        print(keyword, type)
        # result = "response text :" + keyword

        result = request_body(keyword, type) #실제 타입 반환
        # result = "한의사는 도수치료사의 지도 아래, 물리치료사가 틀어진 근육과 척추 등을 바로 잡아주는 물리치료로 빠른 회복을 도모해요." #더미데이터

        return make_response(result, 200)

    # def post(self):
    #     # test = request.json.get()
    #     response = request.json.get("keyword")
    #
    #     print(response)
    #     #SERVICE에서 처리한 값을 Result로 넘겨줌
    #     # result = SortingByFrequency()
    #
    #     return make_response('result', 200)
