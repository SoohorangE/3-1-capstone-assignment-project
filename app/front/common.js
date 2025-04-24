// 대화 기록을 localStorage에서 불러오거나 새로 시작
let conversationHistory = [];
localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));


// UTF-8 safe base64 encode
function encodeBase64(str) {
    return btoa(unescape(encodeURIComponent(str)));
}

// UTF-8 safe base64 decode
function decodeBase64(str) {
    return decodeURIComponent(escape(atob(str)));
}

// LaTeX 수식을 보호하기 위한 마커
function protectLatex(text) {
    return text.replace(/\\\((.*?)\\\)|\\\[(.*?)\\\]|\$\$(.*?)\$\$|\$(.*?)\$/gs, (match) => {
        return `@@LATEX@@${encodeBase64(match)}@@END@@`;
    });
}

// 마킹된 LaTeX 수식을 원래대로 복원
function restoreLatex(text) {
    return text.replace(/@@LATEX@@(.*?)@@END@@/g, (_, encoded) => {
        return decodeBase64(encoded);
    });
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
            let responseText = data.response_result || "❓ 응답이 없어요!";
            const summaryText = data.response_summary || "";

            responseText = protectLatex(responseText)
            let parsedMarkdown = marked.parse(responseText);
            parsedMarkdown = restoreLatex(parsedMarkdown)

            const modelMessageHtml = `<div class="message"><div class="model-message"><strong>모델:</strong><br>${parsedMarkdown}</div></div>`;
            $("#chat-box .message").last().replaceWith(modelMessageHtml)

            // 수식 렌더링
            MathJax.typeset();

            // 스크롤 최신 위치로
            $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);

            // 모델 응답 도움 주게끔 요약본을 추가
            conversationHistory.push({
                role: "assistant",
                content: summaryText
            });

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

    let conversationHistory = [];
    localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));
}