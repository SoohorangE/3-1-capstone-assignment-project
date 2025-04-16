// 대화 기록을 localStorage에서 불러오거나 새로 시작

let conversationHistory = [
    {
        "role": "system",
        "content": "모든 답변은 반드시 한국어로 해주세요, 또한 답변을 최대한 요약 해주세요"
    },
    {
        "role": "system",
        "content": "문장에 수학식이 포함되어 있을 경우 마크다운 형식으로 출력 해주세요"
    }
];

localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));

// 5건 이하로 유지 2건은 시스템 정의 문장이므로 7개가 넘으면 삭제
function trimHistory() {
    if (conversationHistory.length > 7) {
        conversationHistory = conversationHistory.slice(conversationHistory.length - 5);
    }
    localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));
}

function generateText() {
    const prompt = $("#text").val().trim();
    if (!prompt) return;

    // 사용자 메시지 추가
    const userMessageHtml = `
      <div class="message">
        <div class="user-message"><strong>사용자:</strong> ${prompt}</div>
      </div>`;
    $("#chat-box").append(userMessageHtml);

    // 대화 기록에 사용자 메시지 추가
    conversationHistory.push({
        role: "user",
        content: prompt
    });

    trimHistory();

    // 스크롤 최신 위치
    $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);

    // 응답 자리 마련
    const loadingMsg = `<div class="message"><div class="model-message"><strong>모델:</strong> ⏳ 답변 생성중...</div></div>`;
    $("#chat-box").append(loadingMsg);

    // 서버 요청
    fetch("http://127.0.0.1:8000/answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                history: conversationHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            const responseText = data.result || "❓ 응답이 없어요!";

            console.log(responseText);

            let parsedMarkdown = marked.parse(responseText);

            // 파싱된 마크다운을 HTML 템플릿에 삽입
            const modelMessageHtml = `<div class="model-message"><strong>모델:</strong><br>${parsedMarkdown}</div>`;

            $("#chat-box .message").last().replaceWith(modelMessageHtml)

            // 수식 렌더링
            MathJax.typeset();

            // 대화 저장
            conversationHistory.push({
                role: "assistant",
                content: responseText
            });

            // 스크롤 최신 위치로
            $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);

            // 모델 응답도 히스토리에 추가
            conversationHistory.push({
                role: "assistant",
                content: responseText
            });
            trimHistory();
        })
        .catch(error => {
            console.error("Error:", error);
            const errorMessageHtml = `<div class="model-message"><strong>모델:</strong> ⚠️ 에러 발생!</div>`;
            $("#chat-box .message").last().html(errorMessageHtml)
            $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
        });
}

function clearChat() {
    $("#chat-box").empty();  // 대화 기록 삭제

    let conversationHistory = [
        {
            "role": "system",
            "content": "모든 답변은 반드시 한국어로 해주세요, 또한 답변을 최대한 요약 해주세요"
        },
        {
            "role": "system",
            "content": "문장에 수학식이 포함되어 있을 경우 마크다운형식으로 출력 해주세요"
        }
    ];
}