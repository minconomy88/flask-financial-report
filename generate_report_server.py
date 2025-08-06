from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask Financial Report API is running on Render!"

@app.route('/generate-report', methods=['GET'])
def generate_report():
    corp_name = request.args.get('corp_name')
    if not corp_name:
        return jsonify({"error": "Missing 'corp_name' parameter"}), 400

    # 실제 보고서 생성 로직은 생략
    base_url = "https://flask-financial-report.onrender.com"  # 나중에 정확한 URL로 수정
    download_url = f"{base_url}/reports/{corp_name}_report.xlsx"

    return jsonify({
        "corp_name": corp_name,
        "download_url": download_url,
        "message": "📄 Excel report will be available at this link if generated."
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
