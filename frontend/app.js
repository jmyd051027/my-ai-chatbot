
// 1. 백엔드 서버 주소
const API_BASE_URL = "http://127.0.0.1:8000";


// 2. 공통 API 요청 함수
async function apiRequest(path, options = {}) {
    const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...options.headers
            }
        }
    );

    if (!response.ok) {
        throw new Error(`API 오류: ${response.status}`);
    }

    return await response.json();
}


// 3. 수면 통계 불러오기
async function loadSummary() {
    try {
        const summary = await apiRequest(
            "/api/data/summary"
        );

        document.getElementById("stat-count").textContent =
            `${summary.count}개`;

        document.getElementById("stat-mean").textContent =
            summary.mean === null
                ? "-"
                : `${summary.mean}시간`;

        document.getElementById("stat-min").textContent =
            summary.min === null
                ? "-"
                : `${summary.min}시간`;

        document.getElementById("stat-max").textContent =
            summary.max === null
                ? "-"
                : `${summary.max}시간`;

        document.getElementById("stat-period").textContent =
            summary.count > 0
                ? `분석 기간: ${summary.start_date} ~ ${summary.end_date}`
                : "분석 기간: 기록 없음";

        document.getElementById("stat-trend").textContent =
            `수면 추세: ${summary.trend}`;

    } catch (error) {
        console.error("수면 통계 조회 실패:", error);

        document.getElementById("stat-trend").textContent =
            "서버에 연결할 수 없습니다.";
    }
}


// 4. 웹페이지가 열리면 자동 실행
document.addEventListener("DOMContentLoaded", () => {
    loadSummary();
});


// 5. 수면 기록 목록 불러오기
async function loadData() {
    const dataList = document.getElementById("data-list");

    try {
        const records = await apiRequest("/api/data");

        dataList.replaceChildren();

        // 최신 날짜부터 표시
        records.reverse();

        for (const record of records) {
            const row = document.createElement("tr");

            // 날짜, 수면 시간, 메모 표시
            for (const value of [
                record.date,
                `${record.value}시간`,
                record.memo
            ]) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }

            // 수정 버튼
            const editButton = document.createElement("button");
            editButton.textContent = "수정";
            editButton.addEventListener("click", () => {
                editData(record);
            });

            // 삭제 버튼
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "삭제";
            deleteButton.className = "delete-button";

            deleteButton.addEventListener("click", () => {
                deleteData(record.id);
            });

            const actionCell = document.createElement("td");

            actionCell.append(editButton, deleteButton);
            row.appendChild(actionCell);

            dataList.appendChild(row);
        }

    } catch (error) {
        console.error("수면 기록 조회 실패:", error);

        dataList.innerHTML =
            '<tr><td colspan="4">서버에 연결할 수 없습니다.</td></tr>';
    }
}


// 6. 수면 기록 추가 및 수정
async function saveData(event) {
    event.preventDefault();

    const id = document.getElementById("data-id").value;

    const data = {
        date: document.getElementById("sleep-date").value,
        value: Number(
            document.getElementById("sleep-value").value
        ),
        memo: document.getElementById("sleep-memo").value
    };

    const saveButton = document.getElementById("save-button");
    saveButton.disabled = true;

    try {
        if (id) {
            await apiRequest(`/api/data/${id}`, {
                method: "PUT",
                body: JSON.stringify(data)
            });

            alert("수면 기록이 수정되었습니다.");

        } else {
            await apiRequest("/api/data", {
                method: "POST",
                body: JSON.stringify(data)
            });

            alert("수면 기록이 저장되었습니다.");
        }

        resetDataForm();

        await loadData();
        await loadSummary();

    } catch (error) {
        console.error("수면 기록 저장 실패:", error);
        alert("저장에 실패했습니다. 서버 연결을 확인해 주세요.");

    } finally {
        saveButton.disabled = false;
    }
}


// 7. 수면 기록 수정 준비
function editData(record) {
    document.getElementById("data-id").value =
        record.id;

    document.getElementById("sleep-date").value =
        record.date;

    document.getElementById("sleep-value").value =
        record.value;

    document.getElementById("sleep-memo").value =
        record.memo;

    document.getElementById("save-button").textContent =
        "수정 저장";

    document.getElementById("cancel-edit").hidden =
        false;

    document.getElementById("data-form").scrollIntoView({
        behavior: "smooth"
    });
}


// 8. 수면 기록 삭제
async function deleteData(id) {
    const confirmed = confirm(
        "이 수면 기록을 삭제하시겠습니까?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(`/api/data/${id}`, {
            method: "DELETE"
        });

        if (document.getElementById("data-id").value === id) {
            resetDataForm();
        }

        await loadData();
        await loadSummary();

    } catch (error) {
        console.error("수면 기록 삭제 실패:", error);
        alert("삭제에 실패했습니다.");
    }
}


// 9. 입력창 초기화
function resetDataForm() {
    document.getElementById("data-form").reset();

    document.getElementById("data-id").value = "";

    document.getElementById("save-button").textContent =
        "기록 저장";

    document.getElementById("cancel-edit").hidden =
        true;
}


// 10. 수면 기록 관리 기능 연결
document.addEventListener("DOMContentLoaded", () => {
    loadData();

    document.getElementById("data-form")
        .addEventListener("submit", saveData);

    document.getElementById("cancel-edit")
        .addEventListener("click", resetDataForm);
});


// 11. 채팅 말풍선 추가
function addMessage(text, role) {
    const chatMessages =
        document.getElementById("chat-messages");

    const message = document.createElement("div");

    message.className = `message ${role}-message`;
    message.textContent = text;

    chatMessages.appendChild(message);

    // 가장 최근 메시지로 자동 스크롤
    chatMessages.scrollTop =
        chatMessages.scrollHeight;

    return message;
}


// 12. AI에게 질문 전송
async function sendQuestion(event) {
    event.preventDefault();

    const questionInput =
        document.getElementById("question");

    const sendButton =
        document.getElementById("send-button");

    const question = questionInput.value.trim();

    if (!question || sendButton.disabled) {
        return;
    }

    // 사용자 질문 표시
    addMessage(question, "user");

    questionInput.value = "";

    // 중복 전송 방지
    sendButton.disabled = true;
    questionInput.disabled = true;

    sendButton.textContent = "답변 중...";

    // AI 답변 대기 메시지
    const loadingMessage = addMessage(
        "수면 데이터를 분석하고 있습니다...",
        "bot"
    );

    try {
        const result = await apiRequest("/api/chat", {
            method: "POST",
            body: JSON.stringify({
                question: question
            })
        });

        // 실제 AI 답변 표시
        loadingMessage.textContent = result.answer;

        // 이전 대화 목록 자동 갱신
        await loadConversations();

    } catch (error) {
        console.error("AI 질문 전송 실패:", error);

        loadingMessage.textContent =
            "서버에 연결할 수 없거나 답변 처리에 실패했습니다.";

    } finally {
        // 입력창과 전송 버튼 다시 활성화
        sendButton.disabled = false;
        questionInput.disabled = false;

        sendButton.textContent = "전송";

        questionInput.focus();

        const chatMessages =
            document.getElementById("chat-messages");

        chatMessages.scrollTop =
            chatMessages.scrollHeight;
    }
}


// 13. 챗봇 전송 기능 연결
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("chat-form")
        .addEventListener("submit", sendQuestion);
});


// 14. 이전 대화 목록 불러오기
async function loadConversations() {
    const conversationList =
        document.getElementById("conversation-list");

    try {
        const conversations = await apiRequest(
            "/api/conversations"
        );

        conversationList.replaceChildren();

        if (conversations.length === 0) {
            conversationList.textContent =
                "저장된 대화 기록이 없습니다.";
            return;
        }

        for (const conversation of conversations) {
            const item = document.createElement("button");

            item.type = "button";
            item.className = "conversation-item";

            // 질문 표시
            const question = document.createElement("div");
            question.textContent = conversation.question;

            // 대화 생성 시간 표시
            const time = document.createElement("small");

            time.textContent = new Date(
                conversation.created_at
            ).toLocaleString("ko-KR");

            item.append(question, time);

            // 클릭하면 해당 대화 불러오기
            item.addEventListener("click", () => {
                loadConversation(conversation.id);
            });

            conversationList.appendChild(item);
        }

    } catch (error) {
        console.error("대화 목록 조회 실패:", error);

        conversationList.textContent =
            "서버에 연결할 수 없습니다.";
    }
}


// 15. 특정 대화 기록 불러오기
async function loadConversation(id) {
    const sendButton =
        document.getElementById("send-button");

    if (sendButton.disabled) {
        return;
    }

    sendButton.disabled = true;

    try {
        const conversation = await apiRequest(
            `/api/conversations/${id}`
        );

        const chatMessages =
            document.getElementById("chat-messages");

        // 기존 화면의 말풍선 초기화
        chatMessages.replaceChildren();

        // 저장된 질문과 답변 표시
        addMessage(conversation.question, "user");
        addMessage(conversation.answer, "bot");

        // 채팅창으로 화면 이동
        document.querySelector(".chat-section")
            .scrollIntoView({
                behavior: "smooth"
            });

    } catch (error) {
        console.error("대화 불러오기 실패:", error);

        alert("대화 기록을 불러오지 못했습니다.");

    } finally {
        sendButton.disabled = false;
    }
}


// 16. 웹페이지가 열리면 대화 목록 조회
document.addEventListener("DOMContentLoaded", () => {
    loadConversations();
});

