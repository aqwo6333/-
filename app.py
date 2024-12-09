from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import openai
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

openai.api_key = "Your_Openai_api_key"
DRUG_API_KEY = "Your_Drug_api_key"
DRUG_API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
HOSPITAL_API_KEY = "Your_Hospital_api_key"
HOSPITAL_API_URL = "http://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlMdcncListInfoInqire"

DEPARTMENT_CODE_MAP = {
    "내과": "D001",
    "소아청소년과": "D002",
    "산부인과": "D003",
    "정신건강의학과": "D004",
    "외과": "D005",
    "흉부외과": "D006",
    "신경외과": "D007",
    "정형외과": "D008",
    "성형외과": "D009",
    "마취통증의학과": "D010",
    "산부인과": "D011",
    "안과": "D012",
    "이비인후과": "D013",
    "피부과": "D014",
    "비뇨기과": "D015",
    "재활의학과": "D016",
    "마취통증의학과": "D017",
    "영상의학과": "D018",
    "병리과": "D019",
    "진단검사의학과": "D020",
    "방사선종양학과": "D021",
    "핵의학과": "D022",
    "가정의학과": "D023",
    "응급의학과": "D024",
    "직업환경의학과": "D025",
    "결핵과": "D026",
    "예방의학과": "D029"
}

# OpenAI API로 답변 생성 함수
def chat_with_openai(user_input, model="gpt-3.5-turbo", temperature=0.7, max_tokens=500):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "증상 분석 중 오류가 발생했습니다. 다시 시도해 주세요."


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response_text = ""
    openai_response = chat_with_openai(
        f"사용자가 '{user_input}'이라고 말했습니다. 증상에 맞는 진료과목을 추천하고, 필요한 경우 권장되는 행동과 약을 추천해 주세요."
    )
    if any(greeting in user_input.lower() for greeting in ["안녕", "반가워", "고마워"]):
        response_text = "안녕하세요! 무엇을 도와드릴까요? 증상이 있으면 말씀해 주세요."
    else:
        response_text = openai_response

    response_text += "\n\n근처 관련 병원을 조회하시겠어요? (예 / 아니오)"
    # 사용자가 "예"라고 입력한 경우 location_selection으로 이동
    if user_input.strip().lower() == "예":
        return jsonify({"redirect": url_for("location_selection")})
    # 최종 응답 반환
    return jsonify({"response": response_text})

# 진료과목 이름으로 코드 반환
def get_department_code(department_name):
    return DEPARTMENT_CODE_MAP.get(department_name, None)

# 병원 정보 조회 함수
def fetch_hospital_info(city, district, department_name, page_no=1):
    department_code = DEPARTMENT_CODE_MAP.get(department_name)
    if not department_code:
        return f"'{department_name}'에 대한 진료과목 코드가 없습니다."
    try:
        params = {
            "serviceKey": HOSPITAL_API_KEY,
            "Q0": city,  # 도시
            "Q1": district,  # 지역구
            "QD": department_code,  # 진료과목 코드
            "pageNo": page_no,  # 페이지 번호
            "numOfRows": 10,  # 페이지당 항목 수
        }
        response = requests.get(HOSPITAL_API_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        if not items:
            return "해당 지역에 대한 병원 정보를 찾을 수 없습니다."

        hospital_info = []
        for item in items:
            duty_name = item.find("dutyName").text if item.find("dutyName") is not None else "정보 없음"
            duty_addr = item.find("dutyAddr").text if item.find("dutyAddr") is not None else "정보 없음"
            duty_tel = item.find("dutyTel1").text if item.find("dutyTel1") is not None else "정보 없음"
            hospital_info.append(f"병원명: {duty_name}, 주소: {duty_addr}, ☎: {duty_tel}")

        return "\n".join(hospital_info)
    except Exception as e:
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"

# 추천 병원 검색 엔드포인트
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    city = data.get("city")
    district = data.get("district")
    department = data.get("medical_department")
    page_no = data.get("pageNo", 1)

    if not city or not district or not department:
        return jsonify({"response": "도시, 지역구, 진료과목을 모두 선택해주세요."})

    hospital_info = fetch_hospital_info(city, district, department, page_no)
    return jsonify({"response": hospital_info})

# location_selection 페이지 경로 설정
@app.route("/location_selection", methods=["GET", "POST"])
def location_selection():
    return render_template("location_selection.html", all_departments=DEPARTMENT_CODE_MAP)

@app.route("/save_departments", methods=["POST"])
def save_departments():
    departments = request.json.get("departments")
    if departments:
        session["recommended_departments"] = departments
        return jsonify({"success": True})
    return jsonify({"error": "No departments provided"})

@app.route("/drug_information")
def drug_information():
    return render_template("drug_information.html")

@app.route("/search_drug", methods=["POST"])
def search_drug():
    data = request.json
    drug_name = data.get("drugName")
    
    if not drug_name:
        return jsonify({"error": "의약품 이름을 입력해주세요."})
    try:
        params = {
            "serviceKey": DRUG_API_KEY,
            "itemName": drug_name,
            "type": "json",
            "numOfRows": 1
        }
        response = requests.get(DRUG_API_URL, params=params)
        response.raise_for_status()

        # API 응답 처리
        drug_data = response.json()
        if "body" in drug_data and "items" in drug_data["body"] and drug_data["body"]["items"]:
            item = drug_data["body"]["items"][0]
            return jsonify({
                "itemName": item.get("itemName", "N/A"),
                "efcyQesitm": item.get("efcyQesitm", "N/A"),
                "useMethodQesitm": item.get("useMethodQesitm", "N/A"),
                "atpnQesitm": item.get("atpnQesitm", "N/A"),
                "seQesitm": item.get("seQesitm", "N/A"),
                "depositMethodQesitm": item.get("depositMethodQesitm", "N/A")
            })
        else:
            return jsonify({"error": "해당 의약품 정보를 찾을 수 없습니다."})
    except Exception as e:
        print(f"Error fetching drug information: {e}")
        return jsonify({"error": "의약품 정보를 가져오는 데 실패했습니다. 다시 시도해 주세요."})

# 홈페이지 경로 설정
@app.route("/")
def home():
    return render_template("index.html")

# Flask 앱 실행
if __name__ == "__main__":
    app.run(debug=True)
