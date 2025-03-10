# flask import
from flask import Flask, render_template, request
# YOLO model import(모델 실행 파일 import)
from model.model import analyze_acne_by_parts_result

app = Flask(__name__)

# "/" (첫 화면) 경로에서 GET, POST 방식으로 요청을 받음
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return "파일이 없습니다!", 400
    
        file = request.files['file']
        if file.filename == '':
            return "선택된 파일이 없습니다!", 400
    
        try:
            # 모델 실행
            img, results = analyze_acne_by_parts_result(file)
        except Exception as e:
            return f"모델 실행 중 오류 발생: {e}", 500
        # 결과 페이지로 이동
        return render_template("result.html", results=results, filename=file.filename)
    # GET 방식일 경우 index.html 페이지로 이동
    return render_template("index.html")

# Flask 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True) 