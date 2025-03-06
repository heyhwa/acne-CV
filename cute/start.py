from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 메인 페이지
@app.route("/")
def hello():
    return render_template("hello.html")

# 개인정보 입력 페이지
@app.route("/apply")
def apply():
    return render_template("apply.html")

# 등록된 사진 리스트 페이지
@app.route("/list")
def list_page():
    return render_template("list.html")

# 사진 등록 페이지 (이름과 나이를 전달)
@app.route("/applyphoto")
def photo_apply():
    name = request.args.get("name")
    age = request.args.get("age")

    # 콘솔에서 확인용 출력
    print(f"이름: {name}, 나이: {age}")

    # apply_photo.html 페이지로 이동하며, 입력한 이름과 나이를 전달
    return render_template("apply_photo.html", name=name, age=age)

# 사진 업로드 처리
@app.route("/upload_done", methods=["POST"])
def upload_done():
    if 'file' not in request.files:
        return "파일이 없습니다!", 400  # 파일이 포함되지 않은 경우 오류 반환
    
    upload_file = request.files['file']

    if upload_file.filename == '':
        return "선택된 파일이 없습니다!", 400  # 선택된 파일이 없는 경우 오류 반환
    
    # 파일 저장 (고유한 파일명으로 저장하는 것이 좋음)
    file_path = f"static/img/{upload_file.filename}"
    upload_file.save(file_path)

    print(f"파일 저장 완료: {file_path}")

    return redirect(url_for("hello"))  # 업로드 후 메인 페이지로 이동

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)  # debug=True 추가하여 개발 중 오류 메시지 확인 가능
