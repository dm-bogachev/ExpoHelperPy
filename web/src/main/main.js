const host = window.location.hostname;
const RECORDER_URL = `http://${host}/api/recorder`;
const API_URL = `http://${host}/api/database`;
const ROBOT_URL = `http://${host}/api/robot`;
const SETTINGS_URL = `http://${host}/api/settings`;



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
    },
    "20": {
        text: "Обрабатываю видео",
        icon: '<i class="fas fa-cog text-info" title="Обрабатываю видео"></i>',
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
        const showMotor = Number(user.status) == 0; // Показывать только если статус -1, 0 или 1
        const tr = document.createElement('tr');
        tr.className = statusToRowClass(user.status);
        // console.log(`Рендерим пользователя ${user.id} со статусом ${user.status} (${statusToText(user.status)})`);
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
                <button class="btn btn-outline-primary btn-sm w-100 gen-qr-btn" data-link="${encodeURIComponent(user.video_link)}" type="button">
                    <i class="fas fa-qrcode"></i> Сгенерировать QR код
                </button>
                <div>
                    <a href="${user.video_link}" target="_blank" style="font-size:0.95em;">
                    ${user.video_link.substring(user.video_link.lastIndexOf('/') + 1)}
                    </a>
                </div>
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
        // Открытие модалки только по клику на область статуса
        tr.style.cursor = "pointer";
        // Найдём ячейку статуса (4-я по счёту, индексация с 0)
        const statusCell = tr.children[3];
        if (statusCell) {
            statusCell.style.cursor = "pointer";
            statusCell.onclick = (e) => {
            openRecordModal(user);
            e.stopPropagation();
            };
        }
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
    tbody.querySelectorAll('.gen-qr-btn').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            const link = decodeURIComponent(this.dataset.link);
            // Создаём простую модалку для QR
            let modal = document.getElementById('qrSimpleModal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'qrSimpleModal';
                modal.style.position = 'fixed';
                modal.style.top = '0';
                modal.style.left = '0';
                modal.style.width = '100vw';
                modal.style.height = '100vh';
                modal.style.background = 'rgba(0,0,0,0.5)';
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
                modal.style.zIndex = '9999';
                modal.innerHTML = `
                    <div style="background:#fff;padding:24px 24px 12px 24px;border-radius:12px;box-shadow:0 2px 16px #0003;text-align:center;position:relative;">
                        <img id="qrSimpleImg" style="max-width:200px;max-height:200px;display:block;margin:0 auto 12px auto;">
                        <div style="word-break:break-all;font-size:0.95em;">
                            <a id="qrSimpleLink" href="#" target="_blank"></a>
                        </div>
                        <button id="qrSimpleClose" style="position:absolute;top:8px;right:8px;border:none;background:transparent;font-size:1.5em;line-height:1;cursor:pointer;">×</button>
                    </div>
                `;
                document.body.appendChild(modal);
                modal.querySelector('#qrSimpleClose').onclick = () => {
                    modal.style.display = 'none';
                };
                modal.onclick = (ev) => {
                    if (ev.target === modal) modal.style.display = 'none';
                };
            }
            const qrImg = modal.querySelector('#qrSimpleImg');
            const qrLink = modal.querySelector('#qrSimpleLink');
            if (qrImg && qrLink) {
                qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(link)}`;
                qrLink.href = link;
                qrLink.textContent = link;
            }
            modal.style.display = 'flex';
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
        let btns = document.getElementById('robotControlBtns');
        if (!btns) {
            btns = document.createElement('span');
            btns.id = 'robotControlBtns';
            btns.style.marginLeft = '16px';
            if (light && light.parentNode) {
                light.parentNode.insertBefore(btns, light.nextSibling);
            }
        }
        if (light) {
            if (data.connected) {
                light.style.background = '#28a745'; // green
                btns.innerHTML = `
                    <button id="robotHomeBtn" class="btn btn-outline-primary btn-sm me-2">Робота домой</button>
                    <button id="robotServiceBtn" class="btn btn-outline-secondary btn-sm">Робота в сервис</button>
                `;
                document.getElementById('robotHomeBtn').onclick = async () => {
                    await fetch(`${ROBOT_URL}/home`, { method: 'POST' });
                };
                document.getElementById('robotServiceBtn').onclick = async () => {
                    await fetch(`${ROBOT_URL}/service`, { method: 'POST' });
                };
            } else {
                light.style.background = '#dc3545'; // red
                btns.innerHTML = '';
            }
        }
    } catch {
        const light = document.getElementById('robotStatusLight');
        if (light) {
            light.style.background = '#ccc'; // gray (unknown)
        }
        const btns = document.getElementById('robotControlBtns');
        if (btns) btns.innerHTML = '';
    }
}

// Проверяем статус робота при загрузке и далее каждую секунду
checkRobotStatus();
setInterval(checkRobotStatus, 1000);

fetchAndRenderUsers();
setInterval(fetchAndRenderUsers, 1000);

document.addEventListener("DOMContentLoaded", () => {
    // Заменяем ссылки в футере на реальные пути
    const footerLinks = document.querySelectorAll('footer a');
    if (footerLinks.length >= 3) {
        footerLinks[0].href = `http://${host}/api/database/docs`;
        footerLinks[1].href =`http://${host}/api/recorder/docs`;
        footerLinks[2].href = `http://${host}/api/robot/docs`;
        footerLinks[3].href = `http://${host}/api/settings/docs`;
    }

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

    // Обработчик добавления пользователя
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.onsubmit = function(e) {
            e.preventDefault();
            const nameInput = document.getElementById('addUserName');
            const name = nameInput.value.trim();
            if (!name) return;
            fetch(`${API_URL}/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, chat_id: 0, status: 0 })
            }).then(resp => {
                if (resp.ok) {
                    nameInput.value = '';
                    fetchAndRenderUsers();
                } else {
                    alert('Ошибка добавления пользователя');
                }
            });
        };
    }

    loadJsonSettings();
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

async function loadJsonSettings() {
    const container = document.getElementById('jsonSettings');
    container.innerHTML = '<div class="text-muted">Загрузка настроек...</div>';
    // Получаем список файлов
    const resp = await fetch(`${SETTINGS_URL}/configs`);
    const files = await resp.json();
    container.innerHTML = '';

    // Добавляем кнопку "Сохранить все"
    const saveAllBtn = document.createElement('button');
    saveAllBtn.type = 'button';
    saveAllBtn.className = 'btn btn-success btn-sm mb-3';
    saveAllBtn.textContent = 'Сохранить';
    container.appendChild(saveAllBtn);

    // Для хранения ссылок на элементы и содержимое
    const fileGroups = [];

    for (const fname of files) {
        let content = {};
        try {
            const fileResp = await fetch(`${SETTINGS_URL}/configs/${fname}`);
            content = await fileResp.json();
        } catch (e) {
            content = { error: "Ошибка загрузки содержимого" };
        }
        const group = document.createElement('div');
        group.className = 'mb-3';
        group.innerHTML = `<label class="form-label fw-bold">${fname}</label>`;
        const form = document.createElement('form');
        form.className = 'row g-2 align-items-center mb-2';
        Object.entries(content).forEach(([key, value], idx) => {
            const col = document.createElement('div');
            col.className = 'col-12 col-md-6';
            let inputType = typeof value === 'number' ? 'number' : 'text';
            if (typeof value === 'boolean') {
                col.innerHTML = `
                    <label class="form-label me-2">${key}:</label>
                    <input type="checkbox" class="form-check-input" id="json-${fname}-${key}" ${value ? 'checked' : ''}>
                `;
            } else {
                col.innerHTML = `
                    <label class="form-label">${key}:</label>
                    <input type="${inputType}" class="form-control" id="json-${fname}-${key}" value="${value}">
                `;
            }
            // Каждый параметр на новой строке
            col.classList.add('mb-2');
            form.appendChild(col);
        });
        group.appendChild(form);

        // Статус
        var statusDiv = document.createElement('div');
        statusDiv.className = 'json-save-status mt-1 small';
        group.appendChild(statusDiv);

        container.appendChild(group);

        // Добавляем разделитель между группами (кроме последней)
        container.appendChild(document.createElement('hr'));

        // Сохраняем для общей кнопки
        fileGroups.push({ fname, content, statusDiv });

        // Локальная кнопка сохранить
        // const saveBtn = document.createElement('button');
        // saveBtn.type = 'button';
        // saveBtn.className = 'btn btn-primary btn-sm mt-2';
        // saveBtn.textContent = 'Сохранить';
        // group.appendChild(saveBtn);

        // Статус
        statusDiv = document.createElement('div');
        statusDiv.className = 'json-save-status mt-1 small';
        group.appendChild(statusDiv);
        container.appendChild(group);

        // Сохраняем для общей кнопки
        fileGroups.push({ fname, content, statusDiv });

    }

    // Обработчик для общей кнопки "Сохранить все"
    saveAllBtn.onclick = async function() {
        saveAllBtn.disabled = true;
        saveAllBtn.textContent = 'Сохраняю...';
        for (const { fname, content, statusDiv } of fileGroups) {
            let newJson = {};
            Object.entries(content).forEach(([key, value]) => {
                const input = document.getElementById(`json-${fname}-${key}`);
                if (!input) return;
                if (typeof value === 'boolean') {
                    newJson[key] = input.checked;
                } else if (typeof value === 'number') {
                    newJson[key] = input.value === "" ? null : Number(input.value);
                } else {
                    newJson[key] = input.value;
                }
            });
            try {
                const resp = await fetch(`${SETTINGS_URL}/configs/${fname}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(newJson)
                });
                if (resp.ok) {
                    statusDiv.textContent = "Сохранено!";
                    statusDiv.style.color = "green";
                } else {
                    statusDiv.textContent = "Ошибка сохранения";
                    statusDiv.style.color = "red";
                }
            } catch (e) {
                statusDiv.textContent = "Ошибка: " + e;
                statusDiv.style.color = "red";
            }
        }
        saveAllBtn.disabled = false;
        saveAllBtn.textContent = 'Сохранить все';
    };
}
