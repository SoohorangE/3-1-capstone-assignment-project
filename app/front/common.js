// 대화 기록을 localStorage에서 불러오거나 새로 시작

let conversationHistory = [{
    "role": "system",
    "content": "모든 답변은 반드시 한국어로 해주세요, 또한 정확한 정보를 제공해야하며 정확하지 않으면, 틀릴수도 있다고 사용자에게 알려주세요."
}];

localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));

// 30개 이하로 유지
function trimHistory() {
    if (conversationHistory.length > 30) {
        conversationHistory = conversationHistory.slice(conversationHistory.length - 30);
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
            const modelMessageHtml = `<div class="model-message"><strong>모델:</strong> ${responseText}</div>`;
            $("#chat-box .message").last().html(modelMessageHtml)

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
}