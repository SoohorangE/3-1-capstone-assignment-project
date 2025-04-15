# sllmproject2025
캡스톤프로젝트2 과목 세번째 프로젝트, sLLM 만들어보기

---

# 나만의 챗봇 만들기

## 개요

### 모델
- LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct 모델 사용

### 프로젝트에 EXAONE 모델을 채택한 이유?
- `가볍고, 빠르고, 한국어에 적합한 모델.`
- 요즘 뜨는 deepseek, chatgpt와 비교시 거의 비슷하거나, 소폭 우위

### 구성
- FastAPI, html를 통해 실시간 소통 구현
- 이전의 질문과도 실시간으로 연동 가능(30건 이내)

### 실행방법
- main.py를 실행시켜 서버와 모델을 로딩한다.

### 결과물

---
### reference
- LG-Ai: https://www.lgresearch.ai/blog/view?seq=541
- EXAONE Hugging Face : https://huggingface.co/google/gemma-2-2b-it