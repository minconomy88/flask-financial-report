from flask import Flask, request, jsonify
import pandas as pd
import requests
import os

app = Flask(__name__)
API_KEY = '8ba3665e7adee12177138abb35dce39e4a10673e'
CORP_CODES_JSON_URL = 'https://github.com/minconomy88/dart-corp-codes/blob/main/corp_codes_all.json'

# 기업명으로 corp_code 찾기
def get_corp_code(corp_name):
    resp = requests.get(CORP_CODES_JSON_URL)
    codes = resp.json()
    for name, code in codes.items():
        if corp_name in name or name in corp_name:
            return code
    return None

# DART API에서 재무제표 받기
def get_statements(corp_code, year, reprt_code):
    url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    params = {
        'crtfc_key': API_KEY,
        'corp_code': corp_code,
        'bsns_year': year,
        'reprt_code': reprt_code
    }
    res = requests.get(url, params=params)
    return res.json()

@app.route('/generate-report', methods=['GET'])
def generate_report():
    corp_name = request.args.get('corp_name')
    corp_code = get_corp_code(corp_name)

    if not corp_code:
        return jsonify({'error': '기업명을 찾을 수 없습니다.'}), 404

    years = ['2023', '2022', '2021']
    reprt_codes = ['11011', '11012', '11013', '11014']
    all_data = []

    for year in years:
        for code in reprt_codes:
            data = get_statements(corp_code, year, code)
            if data.get('status') == '013':
                continue
            for item in data.get('list', []):
                item['year'] = year
                item['reprt_code'] = code
                all_data.append(item)

    if not all_data:
        return jsonify({'error': '재무제표가 없습니다.'}), 404

    df = pd.DataFrame(all_data)
    os.makedirs('reports', exist_ok=True)
    filename = f'reports/{corp_name}_report.xlsx'
    df.to_excel(filename, index=False)

    return jsonify({
        'download_url': f'https://yourdomain.com/reports/{corp_name}_report.xlsx'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
