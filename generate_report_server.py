from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ✅ 외부 JSON URL (본인의 GitHub 경로로 수정!)
CORP_JSON_URL = "https://raw.githubusercontent.com/minconomy88/flask-financial-report/main/corp_codes_all.json"

@app.route('/')
def home():
    return "✅ Flask Financial Report API is running with external corp code JSON!"

@app.route('/generate-report', methods=['GET'])
def generate_report():
    corp_name = request.args.get('corp_name')
    if not corp_name:
        return jsonify({"error": "Missing 'corp_name' parameter"}), 400

    try:
        response = requests.get(CORP_JSON_URL)
        response.raise_for_status()
        corp_dict = response.json()
    except Exception as e:
        return jsonify({"error": "Failed to load corp_codes_all.json", "detail": str(e)}), 500

    # ✅ 기업명 → 코드 매핑
    corp_code = corp_dict.get(corp_name)
    if not corp_code:
        return jsonify({"error": f"No corp_code found for '{corp_name}'"}), 404

    base_url = "https://flask-financial-report.onrender.com"
    download_url = f"{base_url}/reports/{corp_name}_{corp_code}_report.xlsx"

    return jsonify({
        "corp_name": corp_name,
        "corp_code": corp_code,
        "download_url": download_url,
        "message": "📄 Excel report will be available at this link if generated."
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
