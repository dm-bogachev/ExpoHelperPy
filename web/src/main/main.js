const host = window.location.hostname;
const RECORDER_URL = `http://${host}/api/recorder`;
const API_URL = `http://${host}/api/database`;
const ROBOT_URL = `http://${host}/api/robot`;



const statuses = {
    "-1": {
        text: "Пользователь открыл бот",
        icon: '<i class="fas fa-file-alt text-secondary" title="Создано"></i>',
        class: "status-created"
    },
    "0": {
        text: "Пользователь зарегистрирован",
        icon: '<i class="fas fa-user-plus text-primary" title="Зарегистрирован"></i>',
        class: "status-registered"
    },
    "1": {
        text: "Видео записано",
        icon: '<i class="fas fa-microphone text-warning" title="Записано"></i>',
        class: "status-recorded"
    },
    "2": {
        text: "Видео обработано",
        icon: '<i class="fas fa-cogs text-warning" title="Обрабатывается"></i>',
        class: "status-processed"
    },
    "3": {
        text: "Видео загружено",
        icon: '<i class="fas fa-upload text-purple" style="color:#6610f2" title="Загружено"></i>',
        class: "status-uploaded"
    },
    "4": {
        text: "Ожидание подписки",
        icon: '<i class="fas fa-hourglass-half text-success" title="Ожидание подписки"></i>',
        class: "status-waitsubscription"
    },
    "5": {
        text: "Видео отправлено пользователю",
        icon: '<i class="fas fa-paper-plane text-success" title="Отправлено"></i>',
        class: "status-sent"
    },
    "10": {
        text: "Запись видео!",
        icon: '<i class="fas fa-video text-danger" title="Запись видео!"></i>',
        class: "status-recording"
    }
};

function statusToText(status) {
    return statuses[String(status)]?.text ?? status;
}

function statusToRowClass(status) {
    return statuses[String(status)]?.class ?? "";
}

function renderUsers(users) {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = "";

    const durationInput = document.getElementById('recordDuration');
    let recordDuration = 10;
    if (durationInput && durationInput.value !== "") {
        recordDuration = Math.max(0, parseInt(durationInput.value, 10) || 10);
    }

    users.slice().reverse().forEach(user => {
        const showMotor = Number(user.status) <= 1; // Показывать только если статус -1, 0 или 1
        const tr = document.createElement('tr');
        tr.className = statusToRowClass(user.status);

        tr.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name ?? ""}</td>
            <td>${user.chat_id}</td>
            <td>
                ${statuses[String(user.status)]?.icon ?? ''} 
                <span class="ms-2">${statusToText(user.status)}</span>
            </td>
            <td>
                ${user.video_link ? `
                    <div>
                        <input type="text" class="form-control form-control-sm mb-2" value="${user.video_link}" readonly style="font-size:0.95em;">
                        <button class="btn btn-outline-primary btn-sm w-100 gen-qr-btn" data-link="${encodeURIComponent(user.video_link)}" type="button">
                            <i class="fas fa-qrcode"></i> Сгенерировать QR код
                        </button>
                        <div class="qr-container mt-2"></div>
                    </div>
                ` : ""}
            </td>
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
            openRecordModal(user);
        };
        tbody.appendChild(tr);
    });

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();

            // Используем актуальное значение времени записи
            const durationInput = document.getElementById('recordDuration');
            let recordDuration = 10;
            if (durationInput && durationInput.value !== "") {
                recordDuration = Math.max(0, parseInt(durationInput.value, 10) || 10);
            }

            fetch(`${RECORDER_URL}/start?user_id=${this.dataset.userId}&duration=${recordDuration}`, {
                method: 'POST',
                headers: { 'accept': 'application/json' },
                body: ''
            }).then(response => {
                if (!response.ok) {
                    alert('Ошибка запуска съёмки');
                } else {
                    //alert(`Съёмка запущена на ${recordDuration} секунд`);
                    startCountdown(recordDuration); // ← запуск таймера
                    fetchAndRenderUsers();
                }
            });
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

function openRecordModal(user) {
    const userInfo = `
        <strong>ID:</strong> ${user.id}<br>
        <strong>Имя:</strong> ${user.name ?? ""}<br>
        <strong>Chat ID:</strong> ${user.chat_id}<br>
        <strong>Статус:</strong> ${statuses[String(user.status)]?.icon ?? ''} ${statusToText(user.status)}<br>
        ${user.video_link ? `<strong>Видео:</strong> <a href="${user.video_link}" target="_blank">Ссылка</a><br>` : ""}
    `;
    document.getElementById('userInfo').innerHTML = userInfo;

    const statusButtons = Object.entries(statuses).map(([key, status]) => `
        <button class="btn btn-sm ${String(key) === String(user.status) ? 'btn-primary' : 'btn-outline-primary'} status-btn" 
            data-user-id="${user.id}" data-status="${key}">
            ${status.text}
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

async function checkRobotStatus() {
    try {
        const response = await fetch(`${ROBOT_URL}/status`);
        if (!response.ok) throw new Error();
        const data = await response.json();
        const light = document.getElementById('robotStatusLight');
        if (light) {
            if (data.connected) {
                light.style.background = '#28a745'; // green
            } else {
                light.style.background = '#dc3545'; // red
            }
        }
    } catch {
        const light = document.getElementById('robotStatusLight');
        if (light) {
            light.style.background = '#ccc'; // gray (unknown)
        }
    }
}

// Проверяем статус робота при загрузке и далее каждую секунду
checkRobotStatus();
setInterval(checkRobotStatus, 1000);

fetchAndRenderUsers();
setInterval(fetchAndRenderUsers, 1000);

document.addEventListener("DOMContentLoaded", () => {
    const img = document.querySelector('img[alt="Камера"]');
    if (img) {
        img.src = `http://${host}:3000/camera/mjpeg`;
    }
    // Добавим элемент для таймера, если его нет
    const settingsDiv = document.querySelector('.w-100.mt-4');
    if (settingsDiv && !document.getElementById('countdownTimer')) {
        const timerDiv = document.createElement('div');
        timerDiv.id = 'countdownTimer';
        timerDiv.className = 'text-center my-2 fs-4 fw-bold text-primary';
        settingsDiv.appendChild(timerDiv);
    }

    const durationInput = document.getElementById('recordDuration');
    // Загрузить сохранённое значение
    const savedDuration = localStorage.getItem('recordDuration');
    if (durationInput && savedDuration !== null) {
        durationInput.value = savedDuration;
    }
    // Сохранять при изменении
    if (durationInput) {
        durationInput.addEventListener('input', () => {
            localStorage.setItem('recordDuration', durationInput.value);
        });
    }
});

// Добавим глобальную переменную для таймера
let countdownInterval = null;

function startCountdown(seconds) {
    console.log(`Запуск таймера на ${seconds} секунд`);
    seconds = seconds + 2;
    clearInterval(countdownInterval);
    const timerDiv = document.getElementById('countdownTimer');
    if (!timerDiv) return;
    let remaining = seconds;
    if (remaining <= 0) {
        timerDiv.textContent = '';
        return;
    }
    timerDiv.textContent = `Осталось: ${remaining} сек.`;
    countdownInterval = setInterval(() => {
        remaining--;
        if (remaining > 0) {
            timerDiv.textContent = `Осталось: ${remaining} сек.`;
        } else {
            timerDiv.textContent = '';
            clearInterval(countdownInterval);
        }
    }, 1000);
}
