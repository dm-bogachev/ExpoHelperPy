const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1/api/database"
    : "http://expo-db:8000/api/database";

// Значки для статусов
const statusIcons = {
    "-1": '<i class="fas fa-file-alt text-secondary" title="Создано"></i>',
    "0": '<i class="fas fa-user-plus text-primary" title="Зарегистрирован"></i>',
    "1": '<i class="fas fa-microphone text-warning" title="Записано"></i>',
    "2": '<i class="fas fa-cogs text-warning" title="Обрабатывается"></i>',
    "3": '<i class="fas fa-upload text-purple" style="color:#6610f2" title="Загружено"></i>',
    "4": '<i class="fas fa-hourglass-half text-success" title="Ожидание подписки"></i>',
    "5": '<i class="fas fa-paper-plane text-success" title="Отправлено"></i>'
};

function statusToText(status) {
    const statusList = {
        "-1": "Пользователь открыл бот",
        "0": "Пользователь зарегистрирован",
        "1": "Видео записано",
        "2": "Видео обработано",
        "3": "Видео загружено",
        "4": "Ожидание подписки",
        "5": "Видео отправлено пользователю"
    };
    return statusList[String(status)] ?? status;
}

function statusToRowClass(status) {
    switch (String(status)) {
        case "-1":
            return "status-created";
        case "0":
            return "status-registered";
        case "1":
            return "status-recorded";
        case "2":
            return "status-processed";
        case "3":
            return "status-uploaded";
        case "4":
            return "status-waitsubscription";
        case "5":
            return "status-sent";
        default:
            return "";
    }
}

function renderUsers(users) {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = "";
    users.slice().reverse().forEach(user => {
        const showMotor = Number(user.status) <= 1; // Показывать только если статус -1, 0 или 1
        const tr = document.createElement('tr');
        tr.className = statusToRowClass(user.status);

        tr.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name ?? ""}</td>
            <td>${user.chat_id}</td>
            <td>
                ${statusIcons[String(user.status)] ?? ''} 
                <span class="ms-2">${statusToText(user.status)}</span>
            </td>
            <td>${user.video_link ? `<a href="${user.video_link}" target="_blank">Ссылка</a>` : ""}</td>
            <td>
                ${showMotor ? `
                <button class="btn btn-primary btn-sm action-btn me-2" data-user-id="${user.id}">
                    <i class="fas fa-redo"></i> Мотор!
                </button>
                ` : ""}
                <button class="btn btn-danger btn-sm delete-btn" data-user-id="${user.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        // Открытие модалки по клику на строку
        tr.style.cursor = "pointer";
        tr.onclick = (e) => {
            if (e.target.closest('.delete-btn') || e.target.closest('.action-btn')) return;
            openUserModal(user);
        };
        tbody.appendChild(tr);
    });

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            fetch(`${API_URL}/users/${this.dataset.userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 1 })
            }).then(fetchAndRenderUsers);
        };
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            if (confirm('Удалить пользователя?')) {
                fetch(`${API_URL}/users/${this.dataset.userId}`, {
                    method: 'DELETE'
                }).then(fetchAndRenderUsers);
            }
        };
    });
}

// Открытие модалки и заполнение данными
function openUserModal(user) {
    const userInfo = `
        <strong>ID:</strong> ${user.id}<br>
        <strong>Имя:</strong> ${user.name ?? ""}<br>
        <strong>Chat ID:</strong> ${user.chat_id}<br>
        <strong>Статус:</strong> ${statusIcons[String(user.status)] ?? ''} ${statusToText(user.status)}<br>
        ${user.video_link ? `<strong>Видео:</strong> <a href="${user.video_link}" target="_blank">Ссылка</a><br>` : ""}
    `;
    document.getElementById('userInfo').innerHTML = userInfo;

    // Кнопки статусов
    const statusOptions = [
        { value: -1, text: "Пользователь открыл бот" },
        { value: 0, text: "Пользователь зарегистрирован" },
        { value: 1, text: "Видео записано" },
        { value: 2, text: "Видео обработано" },
        { value: 3, text: "Видео загружено" },
        { value: 4, text: "Ожидание подписки" },
        { value: 5, text: "Видео отправлено пользователю" }
    ];
    const statusButtons = statusOptions.map(opt => `
        <button class="btn btn-sm ${String(opt.value) === String(user.status) ? 'btn-primary' : 'btn-outline-primary'} status-btn" 
            data-user-id="${user.id}" data-status="${opt.value}">
            ${opt.text}
        </button>
    `).join('');
    document.getElementById('statusButtons').innerHTML = statusButtons;

    // Навешиваем обработчики на кнопки
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.onclick = function() {
            const userId = this.dataset.userId;
            const newStatus = this.dataset.status;
            fetch(`${API_URL}/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: Number(newStatus) })
            }).then(() => {
                fetchAndRenderUsers();
                const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('userModal'));
                modal.hide();
            });
        };
    });

    // Открываем модалку
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

async function fetchAndRenderUsers() {
    try {
        const response = await fetch(API_URL + "/users");
        if (!response.ok) throw new Error("Ошибка загрузки пользователей");
        const users = await response.json();
        renderUsers(users);
    } catch (e) {
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = `<tr><td colspan="6">Ошибка загрузки пользователей</td></tr>`;
        console.error(e);
    }
}

fetchAndRenderUsers();
setInterval(fetchAndRenderUsers, 1000);