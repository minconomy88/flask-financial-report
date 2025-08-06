from flask import Flask, request, jsonify, send_file
import requests
import json
import os
from openpyxl import Workbook
from datetime import datetime

app = Flask(__name__)

# ✅ 환경변수 또는 하드코딩으로 DART API KEY 지정
DART_API_KEY = os.environ.get("DART_API_KEY") or "8ba3665e7adee12177138abb35dce39e4a10673e"
CORP_CODES_URL = "https://raw.githubusercontent.com/minconomy88/flask-financial-report/main/corp_codes_all.json"

# 📁 보고서 저장 폴더 생성
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

@app.route("/")
def index():
    return "✅ DART 재무제표 Excel API 서버 정상 작동 중입니다!"

@app.route("/generate-report", methods=["GET"])
def generate_report():
    corp_name = request.args.get("corp_name")
    year = request.args.get("bsns_year", "2023")
    reprt_code = request.args.get("reprt_code", "11011")  # 기본: 사업보고서

    if not corp_name:
        return jsonify({"error": "❌ 'corp_name' 파라미터가 필요합니다."}), 400

    try:
        # 기업명 → corp_code 매핑
        corp_json = requests.get(CORP_CODES_URL).json()
        corp_code = corp_json.get(corp_name)

        if not corp_code:
            return jsonify({"error": f"'{corp_name}'에 대한 corp_code를 찾을 수 없습니다."}), 404

        # ✅ DART API 호출
        dart_url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": corp_code,
            "bsns_year": year,
            "reprt_code": reprt_code,
            "fs_div": "CFS"  # 연결재무제표
        }

        dart_res = requests.get(dart_url, params=params)
        data = dart_res.json()

        if data.get("status") != "013" and data.get("list"):
            # Excel 파일 생성
            wb = Workbook()
            ws = wb.active
            ws.title = "재무제표"

            # 헤더
            headers = list(data["list"][0].keys())
            ws.append(headers)

            # 데이터 행 추가
            for row in data["list"]:
                ws.append([row.get(col, "") for col in headers])

            # 파일 저장
            safe_name = corp_name.replace(" ", "_")
            filename = f"{safe_name}_{corp_code}_{year}.xlsx"
            file_path = os.path.join(REPORT_DIR, filename)
            wb.save(file_path)

            download_url = f"https://flask-financial-report.onrender.com/reports/{filename}"
            return jsonify({
                "corp_name": corp_name,
                "corp_code": corp_code,
                "bsns_year": year,
                "download_url": download_url
            })
        else:
            return jsonify({"error": "📉 DART 재무제표 데이터를 찾을 수 없습니다.", "detail": data.get("message", "")}), 404

    except Exception as e:
        return jsonify({"error": "❌ 예외 발생", "detail": str(e)}), 500

# 📦 보고서 파일 서빙 (Render용)
@app.route("/reports/<filename>")
def serve_report(filename):
    path = os.path.join(REPORT_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
