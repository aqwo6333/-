import requests
import csv
import xml.etree.ElementTree as ET

# CODE_MST API 데이터 가져오기
def fetch_code_mst(api_key, category):
    url = 'http://apis.data.go.kr/B552657/CodeMast/info'
    codes = []
    page_no = 1
    while True:
        params = {
            'serviceKey': api_key,
            'CM_MID': category,  # 진료과목(D000) 또는 기관구분(H000)
            'numOfRows': 50,  # 한 번에 가져올 데이터 개수 (최대값으로 설정)
            'pageNo': page_no  # 페이지 번호
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            if not items:  # 더 이상 데이터가 없으면 중단
                break
            for item in items:
                cm_mid = item.find("cmMid").text if item.find("cmMid") is not None else "N/A"
                cm_mnm = item.find("cmMnm").text if item.find("cmMnm") is not None else "N/A"
                cm_sid = item.find("cmSid").text if item.find("cmSid") is not None else "N/A"
                cm_snm = item.find("cmSnm").text if item.find("cmSnm") is not None else "N/A"
                codes.append([cm_mid, cm_mnm, cm_sid, cm_snm])
            page_no += 1  # 다음 페이지로 이동
        else:
            print(f"CODE_MST API 요청 실패: {response.status_code}")
            break
    return codes

# 데이터 저장 함수
def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='cp949') as file:
        writer = csv.writer(file)
        writer.writerow(["대분류코드", "대분류명", "소분류코드", "소분류명"])
        writer.writerows(data)
    print(f"CSV 파일 저장 완료: {filename}")

# 실행
def main():
    api_key = "B6RhyQU2mn5MQ4o8aE1gHyxHfj7UMiErPkAwm2Dn3Q9iTmVyDpUuXQ1Z8VtY2DzTMuFTCHfaddbzkm52b2mQ3w=="

    # D000 (진료과목) 데이터 가져오기
    print("D000 (진료과목) 데이터를 가져오는 중...")
    d000_data = fetch_code_mst(api_key, "D000")
    save_to_csv(d000_data, "D000_진료과목.csv")

    # H000 (기관구분) 데이터 가져오기
    print("H000 (기관구분) 데이터를 가져오는 중...")
    h000_data = fetch_code_mst(api_key, "H000")
    save_to_csv(h000_data, "H000_기관구분.csv")

if __name__ == "__main__":
    main()
