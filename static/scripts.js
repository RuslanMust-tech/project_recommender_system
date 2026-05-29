// ==================
// Состояние пользователя и корзины
// ==================
let currentUser = null;
let cart = [];
let selectedUtensils = [];
let selectedSauces = [];

// ==================
// API URL
// ==================
const API_URL = "http://127.0.0.1:8001";

// ==================
// DOM элементы
// ==================
const loginBtn = document.getElementById('loginBtn');
const phoneInput = document.getElementById('phone');
const loginModal = document.getElementById('loginModal');
const userPanel = document.getElementById('userPanel');
const userPanelBtn = document.querySelector('.user-panel-btn');
const closeUserPanel = document.getElementById('closeUserPanel');
const cartModal = document.getElementById('cartModal');

// ==================
// Открытие модалки входа
// ==================
document.querySelector('.login').onclick = () => {
  loginModal.style.display = 'flex';
};

// ==================
// Закрытие модалок
// ==================
document.getElementById('closeLogin').onclick = () => loginModal.style.display = 'none';
closeUserPanel.onclick = () => userPanel.style.display = 'none';
document.getElementById('closeCart').onclick = () => cartModal.style.display = 'none';

// ==================
// Вход пользователя
// ==================
loginBtn.addEventListener('click', async () => {
  const phone = phoneInput.value.replace(/\D/g, '');
  if (!phone) return alert('Введите корректный номер телефона');

  try {
    const response = await fetch(`${API_URL}/user/${phone}`);
    if (!response.ok) throw new Error(`Сервер вернул ${response.status}`);
    currentUser = await response.json();

    // Загружаем корзину
    const cartResponse = await fetch(`${API_URL}/cart/${phone}`);
    const cartData = await cartResponse.json();
    cart = cartData.cart || [];
    updateCart();

    loginModal.style.display = 'none';
    alert(`Привет, ${phone}!`);
  } catch (e) {
    console.error(e);
    alert("Не удалось войти: " + e.message);
  }
});

// ==================
// Добавление товара в корзину
// ==================
function addToCart(name, price, img = '', weight = '') {
  const existing = cart.find(item => item.name === name);
  if (existing) existing.qty++;
  else cart.push({ name, price, qty: 1, img, weight });
  updateCart();
}

// ==================
// Обновление корзины
// ==================
function updateCart() {
  const ul = document.getElementById('cart-items');
  ul.innerHTML = '';
  let total = 0;

  if (cart.length === 0) {
    ul.innerHTML = "<li>Корзина пуста</li>";
  } else {
    cart.forEach((item, index) => {
      total += item.price * item.qty;
      const li = document.createElement('li');
      li.className = "cart-item";
      li.innerHTML = `
        ${item.img ? `<img src="${item.img}" alt="${item.name}" class="cart-img">` : ''}
        <div class="cart-item-info">
          <span class="cart-item-name">${item.name}</span>
          <span class="cart-item-weight">${item.weight}</span>
          <span class="cart-item-price">${item.price} ₽</span>
        </div>
        <div class="qty-controls">
          <button onclick="changeQty(${index}, -1)">-</button>
          <span>${item.qty}</span>
          <button onclick="changeQty(${index}, 1)">+</button>
        </div>
        <button class="remove-item" onclick="removeItem(${index})">&times;</button>
      `;
      ul.appendChild(li);
    });
  }

  document.getElementById('cart-total').innerText = total + " ₽";

  // ⚡ Обновляем верхний счетчик корзины
  const cartCountEl = document.getElementById('cart-count');
  if (cartCountEl) cartCountEl.innerText = cart.reduce((sum, item) => sum + item.qty, 0);

  // Приборы
  document.querySelectorAll('.utensils-list .add-utensil').forEach(btn => {
    const name = btn.closest('.utensil-item').dataset.name;
    btn.disabled = selectedUtensils.includes(name);
    btn.innerText = selectedUtensils.includes(name) ? '✓' : '+';
  });

  // Соусы
  document.querySelectorAll('.sauces-list .add-sauce').forEach(btn => {
    const name = btn.closest('.sauce-item').dataset.name;
    btn.disabled = selectedSauces.includes(name);
    btn.innerText = selectedSauces.includes(name) ? '✓' : '+';
  });

  saveCart();
}

// ==================
// Изменение количества
// ==================
function changeQty(index, delta) {
  cart[index].qty += delta;
  if (cart[index].qty <= 0) cart.splice(index, 1);
  updateCart();
}

// ==================
// Удаление товара
// ==================
function removeItem(index) {
  cart.splice(index, 1);
  updateCart();
}

// ==================
// Работа с приборами
// ==================
document.querySelectorAll('.add-utensil').forEach(btn => {
  btn.addEventListener('click', () => {
    const utensilName = btn.closest('.utensil-item').dataset.name;
    if (!selectedUtensils.includes(utensilName)) {
      selectedUtensils.push(utensilName);
      updateCart();
    }
  });
});

// ==================
// Работа с соусами
// ==================
document.querySelectorAll('.add-sauce').forEach(btn => {
  btn.addEventListener('click', () => {
    const sauceItem = btn.closest('.sauce-item');
    const sauceName = sauceItem.dataset.name;
    const saucePrice = parseInt(sauceItem.dataset.price);

    if (!selectedSauces.includes(sauceName)) {
      selectedSauces.push(sauceName);
      cart.push({
        name: sauceName,
        price: saucePrice,
        qty: 1,
        img: sauceItem.querySelector('img').src,
        weight: ''
      });
      updateCart();
    }
  });
});

// ==================
// Сохранение корзины
// ==================
async function saveCart() {
  if (!currentUser) return;
  try {
    await fetch(`${API_URL}/cart`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentUser.phone, cart: cart })
    });
  } catch (e) {
    console.error("Ошибка при сохранении корзины:", e);
  }
}

// ==================
// Checkout / Оформление заказа
// ==================
document.getElementById('checkoutBtn').onclick = async () => {
  if (cart.length === 0) return alert('Корзина пуста');
  if (!currentUser) return alert('Сначала войдите в личный кабинет');

  const total = cart.reduce((sum, item) => sum + item.qty * item.price, 0);
  const order = {
    id: Math.floor(10000000 + Math.random() * 90000000),
    date: new Date().toLocaleString('ru-RU'),
    total,
    payment: 'Оплата через СБП',
    address: 'г. Уфа, ул. Степана Кувыкина, 27',
    items: cart.map(i => `${i.name} x${i.qty}`)
  };

  try {
    await fetch(`${API_URL}/order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: currentUser.phone, order })
    });
    alert(`Ваш заказ оформлен!\n${order.items.join(', ')}`);
  } catch (e) {
    return alert("Ошибка при оформлении заказа: " + e.message);
  }

  cart = [];
  selectedUtensils = [];
  selectedSauces = [];
  updateCart();
};

// ==================
// Личный кабинет
// ==================
userPanelBtn.addEventListener('click', async () => {
  if (!currentUser) return alert('Сначала войдите');

  document.getElementById('userPhone').innerText = currentUser.phone;
  document.getElementById('userId').innerText = "#" + (1).toString().padStart(4,'0');

  try {
    const response = await fetch(`${API_URL}/orders/${currentUser.phone}`);
    const data = await response.json();
    const orders = data.orders || [];

    const historyDiv = document.getElementById('orderHistory');
    historyDiv.innerHTML = '';

    orders.forEach((order) => {
      const card = document.createElement('div');
      card.className = 'order-card';
      card.innerHTML = `
        <div>
          <div class="order-number">#${order.id}</div>
          <div class="order-date">Время готовности<br>${order.date}</div>
          <div class="order-status">Завершен</div>
        </div>
        <div>
          <div class="order-address-title">Адрес кафе</div>
          <div class="order-address">${order.address}</div>
        </div>
        <div>
          <div class="order-price">${order.total} ₽</div>
          <div class="order-payment">${order.payment}</div>
        </div>
      `;
      historyDiv.appendChild(card);
    });

    userPanel.style.display = 'flex';
  } catch (e) {
    console.error("Ошибка при загрузке заказов:", e);
    alert("Не удалось загрузить заказы");
  }
});

// ==================
// Модалка корзины
// ==================
document.querySelector('.cart').onclick = () => {
  updateCart();
  cartModal.style.display = 'flex';
};

// ==================
// Показ меню и фильтры категорий
// ==================
const showMenuBtn = document.getElementById('showMenuBtn');
const productsGrid = document.getElementById('productsGrid');
const categoryFilter = document.getElementById('categoryFilter');

showMenuBtn.addEventListener('click', () => {
  productsGrid.style.display = 'grid';
  categoryFilter.style.display = 'flex';
  productsGrid.scrollIntoView({ behavior: 'smooth' });
  document.querySelectorAll('.product').forEach(p => p.style.display = 'flex');
});

document.querySelectorAll('.category').forEach(catEl => {
  catEl.addEventListener('click', () => {
    const cat = catEl.getAttribute('data-cat');
    document.querySelectorAll('.product').forEach(prod => {
      prod.style.display = (prod.dataset.category === cat) ? 'flex' : 'none';
    });
    document.querySelectorAll('.category').forEach(c => c.classList.remove('active'));
    catEl.classList.add('active');
  });
});