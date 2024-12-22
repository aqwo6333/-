from flask import Flask, request, jsonify, render_template, url_for, session
import openai
import requests
import xml.etree.ElementTree as ET

# Flask 앱 초기화
app = Flask(__name__)

# API 키 및 URL 설정
openai.api_key = "YOUR_OPENAI_API_KEY"  # OpenAI API 키
DRUG_API_KEY = "YOUR_DRUG_API_KEY"  # 약 정보 API 키
DRUG_API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"  # 약 정보 API URL
HOSPITAL_API_KEY = "YOUR_HOSPITAL_API_KEY"  # 병원 정보 API 키
HOSPITAL_API_URL = "http://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlMdcncListInfoInqire"  # 병원 정보 API URL

# 진료과목 코드 맵핑
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

# OpenAI API를 통해 챗봇 응답 생성
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
        # OpenAI 응답 메시지 반환
        return response['choices'][0]['message']['content']
    except Exception as e:
        # 예외 발생 시 오류 메시지 반환
        return "증상 분석 중 오류가 발생했습니다. 다시 시도해 주세요."

# /chat 엔드포인트: 사용자의 입력을 받아 챗봇 응답 반환
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")  # 클라이언트로부터 입력 메시지 수신
    response_text = ""
    # OpenAI API를 사용하여 응답 생성
    openai_response = chat_with_openai(
        f"사용자가 '{user_input}'이라고 말했습니다. 증상에 맞는 진료과목을 추천하고, 필요한 경우 권장되는 행동과 약을 추천해 주세요."
    )
    # 간단한 인사 처리
    if any(greeting in user_input.lower() for greeting in ["안녕", "반가워", "하이", "헬로", "ㅎㅇ"]):
        response_text = "안녕하세요! 무엇을 도와드릴까요? 증상이 있으면 말씀해 주세요."
    else:
        response_text = openai_response

    # 병원 조회 여부 추가 메시지
    response_text += "\n\n근처 관련 병원을 조회하시겠어요? (예 / 아니오)"
    # 사용자가 "예"라고 입력한 경우 리다이렉션
    if user_input.strip().lower() == "예":
        return jsonify({
            "redirect": True,
            "url": "/location_selection"
        })
    # 최종 응답 반환
    return jsonify({"response": response_text})

# 진료과목 이름을 코드로 변환하는 함수
def get_department_code(department_name):
    return DEPARTMENT_CODE_MAP.get(department_name, None)

# 병원 정보를 API로 조회하는 함수
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
        # API 요청
        response = requests.get(HOSPITAL_API_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        if not items:
            return "해당 지역에 대한 병원 정보를 찾을 수 없습니다."

        # 병원 정보를 파싱하여 목록 생성
        hospital_info = []
        for item in items:
            duty_name = item.find("dutyName").text if item.find("dutyName") is not None else "정보 없음"
            duty_addr = item.find("dutyAddr").text if item.find("dutyAddr") is not None else "정보 없음"
            duty_tel = item.find("dutyTel1").text if item.find("dutyTel1") is not None else "정보 없음"
            duty_time = item.find("dutyTime1s").text if item.find("dutyTime1s") is not None else ""
            
            info_string = f"병원명: {duty_name}"
            if duty_addr != "정보 없음":
                info_string += f", 주소: {duty_addr}"
            if duty_tel != "정보 없음":
                info_string += f", ☎: {duty_tel}"
            if duty_time:
                info_string += f", 진료시간: {duty_time}"
            
            hospital_info.append(info_string)

        return "\n".join(hospital_info)
    except Exception as e:
        return f"API 호출 중 오류가 발생했습니다: {str(e)}"

# 병원 추천 엔드포인트
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    city = data.get("city")  # 사용자 입력 도시
    district = data.get("district")  # 사용자 입력 지역구
    department = data.get("medical_department")  # 사용자 입력 진료과목
    page_no = data.get("pageNo", 1)  # 페이지 번호 (기본값 1)

    # 필수 입력 항목 확인
    if not city or not district or not department:
        return jsonify({"response": "도시, 지역구, 진료과목을 모두 선택해주세요."})

    # 병원 정보 조회
    hospital_info = fetch_hospital_info(city, district, department, page_no)
    return jsonify({"response": hospital_info})

# 병원 위치 선택 페이지
@app.route("/location_selection", methods=["GET", "POST"])
def location_selection():
    return render_template("location_selection.html", departments=DEPARTMENT_CODE_MAP)

# 추천된 진료과목 저장
@app.route("/save_departments", methods=["POST"])
def save_departments():
    departments = request.json.get("departments")  # 클라이언트로부터 진료과목 수신
    if departments:
        session["recommended_departments"] = departments
        return jsonify({"success": True})
    return jsonify({"error": "No departments provided"})

# 의약품 정보 페이지
@app.route("/drug_information")
def drug_information():
    return render_template("drug_information.html")

# 서비스 소개 페이지
@app.route("/introduction")
def introduction():
    return render_template("introduction.html")

# 의약품 정보 검색 엔드포인트
@app.route("/search_drug", methods=["POST"])
def search_drug():
    data = request.json
    drug_name = data.get("drugName")  # 사용자 입력 의약품 이름
    
    if not drug_name:
        return jsonify({"error": "의약품 이름을 입력해주세요."})

    try:
        params = {
            "serviceKey": DRUG_API_KEY,
            "itemName": drug_name,
            "type": "json",
            "numOfRows": 1
        }
        # 의약품 정보 API 요청
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

# 홈페이지
@app.route("/")
def home():
    return render_template("index.html")

# Flask 앱 실행
if __name__ == "__main__":
    app.run(debug=True)
