# sllmproject2025
캡스톤프로젝트2 과목 세번째 프로젝트, sLLM 만들어보기

---

# 나만의 챗봇 만들기

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

## 📌 개요

### 🔍 모델
- LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct 모델 사용

### ❓프로젝트에 EXAONE 모델을 채택한 이유?
- **⚡ 가볍고, 빠르고, 🇰🇷 한국어에 적합한 모델.**
- 🔥 요즘 뜨는  Qwen, llama와 비교시 거의 비슷하거나, 소폭 우위

| Models              | MT-Bench | LiveBench | Arena-Hard | AlpacaEval | IFEval | KoMT-Bench[1] | LogicKor |
|---------------------|:--------:|:---------:|:----------:|:----------:|:------:|:-------------:|:--------:|
| **EXAONE 3.5 2.4B** | 7.81     | 33.0      | 48.2       | 37.1       | 73.6   | 7.24          | 8.51     |
| Qwen 2.5 3B         | 7.21     | 25.7      | 26.4       | 17.4       | 60.8   | 5.68          | 5.21     |
| Qwen 2.5 1.5B       | 5.72     | 19.2      | 10.6       | 8.4        | 40.7   | 3.87          | 3.60     |
| Llama 3.2 3B        | 6.94     | 24.0      | 14.2       | 18.7       | 70.1   | 3.16          | 2.86     |
| Gemma 2 2B          | 7.20     | 20.0      | 19.1       | 29.1       | 50.5   | 4.83          | 5.29     |

> **참고:**  
> - `KoMT-Bench[1]`은 한국어 평가 기준 벤치마크 점수입니다.  
> - 점수는 모두 클수록 좋은 성능을 의미합니다.

## ⚙️ 프로젝트 구성

- 🧩 **백엔드**: `FastAPI`
- 🖥️ **프론트엔드**: `HTML` 기반 UI
- 💬 **기능**:  
  - 📝 사용자 질문 기록을 포함해 **맥락 기반 응답** 가능
  - ✨ 또한 문장의 **요약 강조** 기능과, **마크다운** 형식을 활용한 읽기 쉬운 화면 구성
  - 📐다양한 **수학식**을 답변에서 지원 가능.
    
---

## 🧠 Generator 클래스

⚙️ 역할:
사용자의 대화 이력을 바탕으로 자연스러운 답변을 생성하고, 그 내용을 요약해주는 핵심 AI 모듈

🛠️ 핵심 기능:
- 🧾 맥락 인식 응답 생성 – 이전 대화 흐름을 이해하고 그에 맞는 답변 생성
- 📝 요약 기능 – 생성된 응답을 다시 요약해, 3줄 이내 핵심 내용 정리
- ⚡ 자동 디바이스 감지 – CUDA / MPS / CPU 자동 감지 및 최적화
- 🧹 리소스 정리 – 생성 후 GPU/메모리 캐시 및 가비지 컬렉션 처리

---

### 실행방법
1. `main.py` 실행 👉 서버 및 모델 로딩  
2. 브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000) 접속  
3. 실시간 AI 챗봇과 대화 시작!

---

### 결과물
> ### **❓SVM에 대한 질문을 했을떄 결과**<br><br>
![결과](picture/1.png)

> ### **❓ 계산식을 설명 해달라고(**맥락 기반 응답**) 질문 했을때 결과** <br><br>
![결과2](picture/2.png)<br><br>
#### 모델이 앞전의 대화 맥락(SVM에 관한 질문)을 이해하며, 계산식 관련된 표현이 정상적으로 출력됨을 확인할 수 있음.

---

### 개선점
- ⚠️ 3B 모델 특성상 **지식 누락 or 부정확한 응답** 존재  
  - 예: "어느 대학교는 어디에 있어?" → 오답 가능성
- ⏳ **긴 토큰 응답 시 응답 지연 or 짤림 발생**  
- 🧠 `LangChain` 활용 시 맥락 기반 대화 성능 향상 가능하지만,  
  - ⚠️ **메모리 이슈**로 Toy 프로젝트엔 부담  
  - 👉 대화 기록은 프론트엔드에서 구성하여 전달하는 방식으로 전환

---
### reference
- LG-Ai: https://www.lgresearch.ai/blog/view?seq=541
- EXAONE Hugging Face : https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct
---
### License

The model is licensed under [EXAONE AI Model License Agreement 1.1 - NC](LICENSE.txt)
