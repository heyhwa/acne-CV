# Flask 및 SQLAlchemy import
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from model.model import analyze_acne_by_parts_result  # YOLO 모델

# Flask 앱 생성
app = Flask(__name__)

# 업로드 폴더 설정
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# SQLite 데이터베이스 설정
DATABASE_URL = "sqlite:///acne_analysis.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# 데이터베이스 테이블 정의 (필요한 컬럼만 유지)
class AcneAnalysis(Base):
    __tablename__ = "acne_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # 업로드 날짜
    total_acne_count = Column(Integer, nullable=False)  # 총 여드름 개수
    max_acne_part = Column(String, nullable=False)  # 가장 여드름이 많은 부위
    cause_organ = Column(String, nullable=False)  # 원인이 되는 장기 추가

# 데이터베이스 변경 적용
Base.metadata.drop_all(engine)  # 기존 테이블 삭제
Base.metadata.create_all(engine)  # 새 테이블 생성


# ✅ 원인이 되는 장기 매핑 (여드름 부위별 원인 장기)
ACNE_CAUSE_MAPPING = {
    "이마": "스트레스",
    "코": "비장",
    "왼쪽볼": "간",
    "오른쪽볼": "폐",
    "턱": "신장"
}

# 분석 결과 저장 함수 (수정됨)
def add_acne_analysis(total_acne_count, max_acne_part):
    session = SessionLocal()

    # ✅ 원인이 되는 장기 찾기
    cause_organ = ACNE_CAUSE_MAPPING.get(max_acne_part, "알 수 없음")

    # ✅ 업로드 날짜 저장
    uploaded_at = datetime.utcnow()

    new_entry = AcneAnalysis(
        uploaded_at=uploaded_at,
        total_acne_count=total_acne_count,
        max_acne_part=max_acne_part,
        cause_organ=cause_organ  # 원인 장기 저장
    )
    session.add(new_entry)
    session.commit()
    session.close()

    print(f"✅ 분석 결과 저장 완료: {uploaded_at}, {max_acne_part} 부위에 뾰루지 (원인: {cause_organ})")

# ✅ 데이터베이스 생성
Base.metadata.create_all(engine)

# 📌 메인 페이지 (파일 업로드)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            return "파일이 없습니다!", 400

        file = request.files['file']
        if file.filename == '':
            return "선택된 파일이 없습니다!", 400

        try:
            # 파일 저장
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # ✅ AI 모델 실행 (파일을 다시 열어서 전달)
            with open(file_path, "rb") as img_file:
                img, results = analyze_acne_by_parts_result(img_file)

            # 분석 결과 정리
            total_acne_count = results["total_acne_count"]
            max_acne_part = results["max_acne_part"]
            acne_count_by_part = results["acne_count_by_part"]

            # 결과 페이지로 이동
            return render_template("result.html",
                                   results={
                                       "total_acne_count": total_acne_count,
                                       "max_acne_part": max_acne_part,
                                       "acne_count_by_part": acne_count_by_part,
                                       "image_path": file_path
                                   },
                                   filename=filename)
        except Exception as e:
            return f"모델 실행 중 오류 발생: {e}", 500

    return render_template("index.html")

# 📌 ✅ 분석 결과 저장 API (AJAX 요청 처리) → **여기에 추가!**
@app.route("/save_result", methods=["POST"])
def save_result():
    data = request.json
    total_acne_count = data.get("total_acne_count")
    max_acne_part = data.get("max_acne_part")

    if total_acne_count is None or max_acne_part is None:
        return jsonify({"error": "저장할 데이터가 부족합니다."}), 400

    # ✅ 분석 결과 저장 (원인 장기 포함)
    add_acne_analysis(total_acne_count, max_acne_part)

    return jsonify({"message": "분석 결과가 성공적으로 저장되었습니다!"})

# Flask 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
