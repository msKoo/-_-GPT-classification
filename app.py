from flask import Flask  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api  # Api 구현을 위한 Api 객체 import

from view.analysis_view import Analysis

from view.api.textGen_view import Generator
from view.api.repu_view import Reputation



app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app, version='1.0', title="saso_nlp",
          description="REST_API Server")

api.add_namespace(Analysis, '/analysis') #평판분석
api.add_namespace(Generator, '/api/gen') #문장생성
api.add_namespace(Reputation, '/api/repu') #문장분석


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

