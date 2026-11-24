
// 1. 백엔드 서버 주소
const API_BASE_URL = "https://sleep-ai-backend.onrender.com";

// 접근 비밀번호 임시 저장
let accessKey = "";


// 2. 공통 API 요청 함수
async function apiRequest(path, options = {}) {
    if (!accessKey) {
        throw new Error("접근 비밀번호를 입력해 주세요.");
    }

    const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
            ...options,
            cache: "no-store",
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
                "X-Access-Key": accessKey
            }
        }
    );

    if (response.status === 401) {
        throw new Error("접근 비밀번호가 올바르지 않습니다.");
    }

    if (response.status === 503) {
        throw new Error("서버 접근 설정이 완료되지 않았습니다.");
    }

    if (!response.ok) {
        throw new Error(`API 오류: ${response.status}`);
    }

    return await response.json();
}


// 3. 서비스 기능 활성화 및 비활성화
function setServiceEnabled(enabled) {
    const sections = document.querySelectorAll(
        ".summary-section, .chat-section, .data-section, .history-section"
    );

    for (const section of sections) {
        section.style.display = enabled ? "" : "none";
    }
}


// 4. 접근 비밀번호 인증
async function authenticate(event) {
    event.preventDefault();

    const keyInput = document.getElementById("access-key");
    const authButton = document.getElementById("auth-button");
    const authStatus = document.getElementById("auth-status");

    const enteredKey = keyInput.value.trim();

    if (!enteredKey || authButton.disabled) {
        return;
    }

    accessKey = enteredKey;

    authButton.disabled = true;
    keyInput.disabled = true;
    authButton.textContent = "접속 확인 중...";

    authStatus.className = "";
    authStatus.textContent = "서버에 접속하고 있습니다...";

    try {
        // 서버에서 접근 비밀번호 확인
        const summary = await apiRequest("/api/data/summary");

        authStatus.className = "success";
        authStatus.textContent =
            "접속에 성공했습니다. Sleep AI를 이용해 주세요!";

        keyInput.value = "";
        authButton.textContent = "접속 완료";

        // 인증 성공 후 서비스 표시
        setServiceEnabled(true);

        // 수면 통계 및 데이터 불러오기
        renderSummary(summary);

        await Promise.all([
            loadData(),
            loadConversations()
        ]);

    } catch (error) {
        accessKey = "";

        setServiceEnabled(false);

        authStatus.className = "error";

        if (error instanceof TypeError) {
            authStatus.textContent =
                "서버에 연결할 수 없습니다. 서버 상태를 확인해 주세요.";
        } else {
            authStatus.textContent = error.message;
        }

        authButton.disabled = false;
        keyInput.disabled = false;
        authButton.textContent = "접속하기";

        keyInput.value = "";
        keyInput.focus();
    }
}


// 5. 수면 통계 화면 표시
function renderSummary(summary) {
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
}


// 6. 수면 통계 불러오기
async function loadSummary() {
    try {
        const summary = await apiRequest(
            "/api/data/summary"
        );

        renderSummary(summary);

    } catch (error) {
        console.error("수면 통계 조회 실패:", error);

        document.getElementById("stat-trend").textContent =
            error.message;
    }
}


// 7. 수면 기록 목록 불러오기
async function loadData() {
    const dataList = document.getElementById("data-list");

    try {
        const records = await apiRequest("/api/data");

        dataList.replaceChildren();

        if (records.length === 0) {
            dataList.innerHTML =
                '<tr><td colspan="4">저장된 수면 기록이 없습니다.</td></tr>';
            return;
        }

        // 최신 날짜부터 표시
        records.reverse();

        for (const record of records) {
            const row = document.createElement("tr");

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
            editButton.type = "button";
            editButton.textContent = "수정";

            editButton.addEventListener("click", () => {
                editData(record);
            });

            // 삭제 버튼
            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
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
            '<tr><td colspan="4">수면 기록을 불러오지 못했습니다.</td></tr>';
    }
}


// 8. 수면 기록 추가 및 수정
async function saveData(event) {
    event.preventDefault();

    if (!accessKey) {
        alert("먼저 서비스에 접속해 주세요.");
        return;
    }

    const id = document.getElementById("data-id").value;

    const data = {
        date: document.getElementById("sleep-date").value,
        value: Number(
            document.getElementById("sleep-value").value
        ),
        memo: document.getElementById("sleep-memo").value
    };

    const saveButton = document.getElementById("save-button");

    if (saveButton.disabled) {
        return;
    }

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

        alert(`저장 실패: ${error.message}`);

    } finally {
        saveButton.disabled = false;
    }
}


// 9. 수면 기록 수정 준비
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


// 10. 수면 기록 삭제
async function deleteData(id) {
    if (!accessKey) {
        alert("먼저 서비스에 접속해 주세요.");
        return;
    }

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

        alert(`삭제 실패: ${error.message}`);
    }
}


// 11. 입력창 초기화
function resetDataForm() {
    document.getElementById("data-form").reset();

    document.getElementById("data-id").value = "";

    document.getElementById("save-button").textContent =
        "기록 저장";

    document.getElementById("cancel-edit").hidden =
        true;
}


// 12. 채팅 말풍선 추가
function addMessage(text, role) {
    const chatMessages =
        document.getElementById("chat-messages");

    const message = document.createElement("div");

    message.className = `message ${role}-message`;
    message.textContent = text;

    chatMessages.appendChild(message);

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

    return message;
}


// 13. AI에게 질문 전송
async function sendQuestion(event) {
    event.preventDefault();

    if (!accessKey) {
        alert("먼저 서비스에 접속해 주세요.");
        return;
    }

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
            `답변 처리에 실패했습니다. ${error.message}`;

    } finally {
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

            const question = document.createElement("div");
            question.textContent = conversation.question;

            const time = document.createElement("small");

            time.textContent = new Date(
                conversation.created_at
            ).toLocaleString("ko-KR");

            item.append(question, time);

            item.addEventListener("click", () => {
                loadConversation(conversation.id);
            });

            conversationList.appendChild(item);
        }

    } catch (error) {
        console.error("대화 목록 조회 실패:", error);

        conversationList.textContent =
            "대화 기록을 불러오지 못했습니다.";
    }
}


// 15. 특정 대화 기록 불러오기
async function loadConversation(id) {
    const sendButton =
        document.getElementById("send-button");

    if (!accessKey || sendButton.disabled) {
        return;
    }

    sendButton.disabled = true;

    try {
        const conversation = await apiRequest(
            `/api/conversations/${id}`
        );

        const chatMessages =
            document.getElementById("chat-messages");

        chatMessages.replaceChildren();

        addMessage(conversation.question, "user");
        addMessage(conversation.answer, "bot");

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


// 16. 웹페이지 초기 설정
document.addEventListener("DOMContentLoaded", () => {

    // 인증 전에는 서비스 화면 숨기기
    setServiceEnabled(false);

    // 접근 비밀번호 인증 연결
    document.getElementById("auth-form")
        .addEventListener("submit", authenticate);

    // 수면 기록 저장 기능 연결
    document.getElementById("data-form")
        .addEventListener("submit", saveData);

    // 수면 기록 수정 취소 기능 연결
    document.getElementById("cancel-edit")
        .addEventListener("click", resetDataForm);

    // AI 챗봇 전송 기능 연결
    document.getElementById("chat-form")
        .addEventListener("submit", sendQuestion);
});
