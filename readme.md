<p align="center">
  <img width="360px;" src="./path/logo360.png" alt="메인페이지"/>
</p>


</p>
</p>
<h1 align="middle">AIHC</h1>
<h3 align="middle">AI를 활용한 건강 챗봇</h3>

<br/>

## Project Overview
- AI가 해당 증상에 맞는 응급처치 방법을 사용자에게 빠르고 효율적으로 응급 정보를 제공. 
- 적절한 병원(일반 내과, 정형외과 등)을 추천


---
## 🌟 주요 기능
- [x] 챗봇을 통해 증상분석을 하고, 병원 추천 및 조회
- [x] 지역별, 진료과목별 병원 조회
- [x] 자신이 복용하는 약의 정보를 검색

---

## 🖼️ 스크린샷
![메인 화면](path/mainscreen.png) 

---
## 🛠️ 기술 스택
- **개발환경:** Google Colab, VSCode  
- **프론트엔드:** HTML, CSS  
- **백엔드:** Flask, Node.js, Python  
- **사용 라이브러리:** OpenAI, Requests, xml.etree.ElementTree  
- **사용 API:**  
  - [식품의약품안전처_의약품개요정보(e약은요)](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15075057)  
  - [국립중앙의료원_전국 병·의원 찾기 서비스](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000736)  
  - [국립중앙의료원_코드마스터 정보 조회 서비스](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000445)  

---

## 🚀 설치 및 실행 방법
1. 이 프로젝트를 클론합니다.
   ```bash
   git clone https://github.com/username/project-name.git
   cd project-name
