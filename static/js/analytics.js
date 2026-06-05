const API = `${window.location.origin}/api/v1/recommendations`;

async function request(path) {
    const response = await fetch(`${API}${path}`);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
}

function money(value) {
    return `${Number(value || 0).toLocaleString("ru-RU")} ₽`;
}

function renderMetrics(metrics) {
    const labels = [
        ["Пользователи", metrics.total_users],
        ["Заказы", metrics.total_orders],
        ["Строки Order", metrics.total_order_rows],
        ["Средний размер", metrics.avg_items_per_order],
    ];
    document.getElementById("metrics").innerHTML = labels.map(([label, value]) => `
        <div class="metric">
            <span>${label}</span>
            <strong>${value}</strong>
        </div>
    `).join("");
}

function drawBarChart(canvasId, rows, labelKey, valueKey, color) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext("2d");
    const ratio = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = Number(canvas.getAttribute("height"));
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    ctx.scale(ratio, ratio);
    ctx.clearRect(0, 0, width, height);

    const data = rows.slice(0, 12);
    const max = Math.max(...data.map(row => Number(row[valueKey] || 0)), 1);
    const pad = 34;
    const gap = 8;
    const barWidth = (width - pad * 2 - gap * (data.length - 1)) / Math.max(data.length, 1);

    ctx.strokeStyle = "#d9e2ec";
    ctx.beginPath();
    ctx.moveTo(pad, height - pad);
    ctx.lineTo(width - pad, height - pad);
    ctx.stroke();

    data.forEach((row, index) => {
        const value = Number(row[valueKey] || 0);
        const barHeight = (height - pad * 2) * value / max;
        const x = pad + index * (barWidth + gap);
        const y = height - pad - barHeight;
        ctx.fillStyle = color;
        ctx.fillRect(x, y, Math.max(barWidth, 2), barHeight);
        ctx.fillStyle = "#1f2933";
        ctx.font = "12px Arial";
        ctx.textAlign = "center";
        ctx.fillText(value, x + barWidth / 2, Math.max(y - 6, 12));
        ctx.save();
        ctx.translate(x + barWidth / 2, height - 8);
        ctx.rotate(-Math.PI / 5);
        ctx.fillStyle = "#52606d";
        ctx.fillText(String(row[labelKey]).slice(0, 16), 0, 0);
        ctx.restore();
    });
}

function renderTopDishes(items) {
    document.getElementById("topDishes").innerHTML = items.map(item => `
        <div class="row">
            <div>
                <strong>${item.name}</strong>
                <small>${item.category} · ${money(item.price_rub)}</small>
            </div>
            <b>${item.orders_count}</b>
        </div>
    `).join("");
}

function renderRules(rules) {
    const rows = rules.map(rule => `
        <div class="table-row">
            <div>${rule.source.name}<small>${rule.source.category}</small></div>
            <div>${rule.target.name}<small>${rule.target.category}</small></div>
            <div>${rule.lift}</div>
            <div>${rule.confidence}</div>
            <div>${rule.support}</div>
        </div>
    `).join("");
    document.getElementById("rulesTable").innerHTML = `
        <div class="table-row table-head">
            <div>Если купили</div>
            <div>Предложить</div>
            <div>Lift</div>
            <div>Conf.</div>
            <div>Supp.</div>
        </div>
        ${rows || '<div class="muted">Недостаточно совместных заказов.</div>'}
    `;
}

async function loadOverview() {
    const data = await request("/analytics/overview?limit=12");
    renderMetrics(data.metrics);
    drawBarChart("categoryChart", data.category_sales, "category", "orders_count", "#d92323");
    drawBarChart("sizeChart", data.order_size_distribution, "items_count", "orders_count", "#2f80ed");
    renderTopDishes(data.top_dishes);
    renderRules(data.association_rules);
}

async function searchDishes() {
    const q = document.getElementById("dishInput").value.trim();
    const data = await request(`/analytics/search-dishes?q=${encodeURIComponent(q)}&limit=20`);
    const select = document.getElementById("dishSelect");
    select.innerHTML = data.items.map(item => `
        <option value="${item.id}">${item.name}</option>
    `).join("");
}

async function loadUser() {
    const phone = document.getElementById("phoneInput").value.trim();
    const panel = document.getElementById("userPanel");
    if (!phone) {
        panel.textContent = "Введите телефон.";
        return;
    }
    const data = await request(`/analytics/users/${encodeURIComponent(phone)}`);
    if (!data.user) {
        panel.textContent = "Пользователь не найден.";
        return;
    }
    const dishes = data.top_dishes.map(item => `
        <div class="row">
            <div><strong>${item.name}</strong><small>${item.category}</small></div>
            <b>${item.orders_count}</b>
        </div>
    `).join("");
    const orders = data.orders.slice(0, 8).map(order => `
        <div class="row">
            <div><strong>#${order.order_id}</strong><small>${order.items_count} поз.</small></div>
            <b>${money(order.total_rub)}</b>
        </div>
    `).join("");
    panel.innerHTML = `
        <div class="row"><div><strong>${data.user.phone_number}</strong><small>ID ${data.user.id}</small></div><b>${data.orders.length}</b></div>
        <h3>Любимые блюда</h3>
        ${dishes || '<div class="muted">Нет покупок.</div>'}
        <h3>Последние заказы</h3>
        ${orders || '<div class="muted">Нет заказов.</div>'}
    `;
}

async function loadDish() {
    const dishId = document.getElementById("dishSelect").value;
    const panel = document.getElementById("dishPanel");
    if (!dishId) {
        panel.textContent = "Выберите блюдо.";
        return;
    }
    const data = await request(`/analytics/dishes/${dishId}`);
    if (!data.dish) {
        panel.textContent = "Блюдо не найдено.";
        return;
    }
    const related = data.bought_with.map(item => `
        <div class="row">
            <div><strong>${item.name}</strong><small>${item.category} · ${money(item.price_rub)}</small></div>
            <b>${item.co_orders}</b>
        </div>
    `).join("");
    panel.innerHTML = `
        <div class="row">
            <div><strong>${data.dish.name}</strong><small>${data.dish.category}</small></div>
            <b>${data.orders_count}</b>
        </div>
        ${related || '<div class="muted">Совместных покупок пока нет.</div>'}
    `;
}

function bindEvents() {
    document.getElementById("reloadBtn").addEventListener("click", loadOverview);
    document.getElementById("loadUserBtn").addEventListener("click", loadUser);
    document.getElementById("loadDishBtn").addEventListener("click", loadDish);
    document.getElementById("dishInput").addEventListener("input", () => {
        clearTimeout(window.__dishSearchTimer);
        window.__dishSearchTimer = setTimeout(searchDishes, 250);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    await Promise.all([loadOverview(), searchDishes()]);
});
