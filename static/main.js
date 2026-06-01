// components.js - UI компоненты
class Component {
    constructor(container) {
        this.container = container;
    }

    render() {
        // To be overridden
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
        }
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }
}

class ProductsGrid extends Component {
    constructor(container, store) {
        super(container);
        this.store = store;
        this.currentCategory = null;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            this.renderProducts(state.products);
        });
    }

    renderProducts(products) {
        if (!this.container) return;

        let filteredProducts = products;
        if (this.currentCategory) {
            filteredProducts = products.filter(p => p.category === this.currentCategory);
        }

        this.container.innerHTML = filteredProducts.map(product => `
            <div class="product" data-category="${product.category}" data-product-id="${product.id}">
                <img src="${product.image}" alt="${product.name}" loading="lazy">
                <div class="labels">
                    ${product.labels.map(label => `
                        <span class="label ${label.type}">${label.text}</span>
                    `).join('')}
                </div>
                <strong>${product.name}</strong>
                <p>${product.weight}</p>
                <div class="product-price">${product.price} ₽</div>
                <button onclick="window.productsGrid.addToCart(${product.id})">
                    От ${product.price} ₽ →
                </button>
            </div>
        `).join('');
    }

    async addToCart(productId) {
        const product = this.store.state.products.find(p => p.id === productId);
        if (product) {
            await this.store.addToCart(product);
            this.showNotification(`${product.name} добавлен в корзину`);
        }
    }

    filterByCategory(category) {
        this.currentCategory = category;
        this.renderProducts(this.store.state.products);
    }

    showNotification(message) {
        // Можно добавить toast-уведомление
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

class CategoriesFilter extends Component {
    constructor(container, store, onCategorySelect) {
        super(container);
        this.store = store;
        this.onCategorySelect = onCategorySelect;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            this.renderCategories(state.categories);
        });
    }

    renderCategories(categories) {
        if (!this.container) return;

        this.container.innerHTML = categories.map(category => `
            <div class="category" data-cat="${category.name}">
                ${category.name}
                ${category.count ? `<span class="category-count">(${category.count})</span>` : ''}
            </div>
        `).join('');

        // Добавляем обработчики
        this.container.querySelectorAll('.category').forEach(el => {
            el.addEventListener('click', () => {
                const category = el.dataset.cat;
                this.onCategorySelect(category);

                // Активный класс
                this.container.querySelectorAll('.category').forEach(c => c.classList.remove('active'));
                el.classList.add('active');
            });
        });
    }
}

class CartComponent extends Component {
    constructor(container, store) {
        super(container);
        this.store = store;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            this.renderCart(state);
            this.updateCartCount(state.cart);
        });
    }

    renderCart(state) {
        if (!this.container) return;

        const { cart, selectedUtensils, selectedSauces, utensils, sauces } = state;
        const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

        // Рендерим товары
        const cartItemsHtml = cart.length === 0
            ? '<li>Корзина пуста</li>'
            : cart.map((item, index) => `
                <li class="cart-item" data-item-id="${item.id}">
                    ${item.img ? `<img src="${item.img}" alt="${item.name}" class="cart-img">` : ''}
                    <div class="cart-item-info">
                        <span class="cart-item-name">${item.name}</span>
                        <span class="cart-item-weight">${item.weight}</span>
                        <span class="cart-item-price">${item.price} ₽</span>
                    </div>
                    <div class="qty-controls">
                        <button onclick="window.cartComponent.changeQuantity(${item.id}, -1)">-</button>
                        <span>${item.quantity}</span>
                        <button onclick="window.cartComponent.changeQuantity(${item.id}, 1)">+</button>
                    </div>
                    <button class="remove-item" onclick="window.cartComponent.removeItem(${item.id})">&times;</button>
                </li>
            `).join('');

        // Рендерим приборы
        const utensilsHtml = utensils.map(utensil => `
            <div class="utensil-item" data-utensil-id="${utensil.id}">
                <img src="${utensil.image}" alt="${utensil.name}">
                <div class="utensil-info">
                    <span>${utensil.name}</span>
                    <strong class="utensil-price">${utensil.price} ₽</strong>
                </div>
                <button class="add-utensil" ${selectedUtensils.includes(utensil.id) ? 'disabled' : ''}
                        onclick="window.cartComponent.addUtensil(${utensil.id})">
                    ${selectedUtensils.includes(utensil.id) ? '✓' : '+'}
                </button>
            </div>
        `).join('');

        // Рендерим соусы
        const saucesHtml = sauces.map(sauce => `
            <div class="sauce-item" data-sauce-id="${sauce.id}">
                <img src="${sauce.image}" alt="${sauce.name}">
                <div class="sauce-info">
                    <strong>${sauce.price} ₽</strong>
                    <span>${sauce.name}</span>
                </div>
                <button class="add-sauce" ${selectedSauces.includes(sauce.id) ? 'disabled' : ''}
                        onclick="window.cartComponent.addSauce(${sauce.id})">
                    ${selectedSauces.includes(sauce.id) ? '✓' : '+'}
                </button>
            </div>
        `).join('');

        this.container.innerHTML = `
            <h2>Корзина</h2>
            <ul id="cart-items" class="cart-items">${cartItemsHtml}</ul>
            
            <div class="cart-section utensils-section">
                <h3>Приборы</h3>
                <div class="utensils-list">${utensilsHtml}</div>
                <p class="eco-note">Спасибо, что заботитесь об экологии и не заказываете приборы!</p>
            </div>
            
            <div class="cart-section sauces-section">
                <h3>Не забудьте добавки и соусы</h3>
                <div class="sauces-list">${saucesHtml}</div>
            </div>
            
            <div class="cart-footer">
                <strong>${total} ₽</strong>
                <button id="checkoutBtn">Оформить заказ</button>
            </div>
        `;

        // Добавляем обработчик оформления заказа
        const checkoutBtn = this.container.querySelector('#checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.onclick = () => this.checkout();
        }
    }

    updateCartCount(cart) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        const cartCountEl = document.getElementById('cart-count');
        if (cartCountEl) {
            cartCountEl.textContent = totalItems;
        }
    }

    async changeQuantity(productId, delta) {
        await this.store.updateCartItemQuantity(productId, delta);
    }

    async removeItem(productId) {
        await this.store.removeFromCart(productId);
    }

    async addUtensil(utensilId) {
        const utensil = this.store.state.utensils.find(u => u.id === utensilId);
        if (utensil) {
            await this.store.addUtensil(utensil);
            this.renderCart(this.store.state);
        }
    }

    async addSauce(sauceId) {
        const sauce = this.store.state.sauces.find(s => s.id === sauceId);
        if (sauce) {
            await this.store.addSauce(sauce);
            this.renderCart(this.store.state);
        }
    }

    async checkout() {
        if (this.store.state.cart.length === 0) {
            alert('Корзина пуста');
            return;
        }

        if (!this.store.state.currentUser) {
            alert('Сначала войдите в личный кабинет');
            return;
        }

        try {
            const order = await this.store.createOrder();
            alert(`Ваш заказ оформлен!\nНомер заказа: ${order.id}\nСумма: ${order.total} ₽`);
            // Закрываем модалку корзины
            const cartModal = document.getElementById('cartModal');
            if (cartModal) cartModal.style.display = 'none';
        } catch (error) {
            alert('Ошибка при оформлении заказа: ' + error.message);
        }
    }
}

class UserPanel extends Component {
    constructor(container, store) {
        super(container);
        this.store = store;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            if (this.container.style.display === 'flex') {
                this.renderUserPanel(state);
            }
        });
    }

    async show() {
        if (!this.store.state.currentUser) {
            alert('Сначала войдите');
            return;
        }

        await this.loadOrders();
        this.renderUserPanel(this.store.state);
        this.container.style.display = 'flex';
    }

    async loadOrders() {
        if (!this.store.state.currentUser) return;

        try {
            const data = await api.getOrders(this.store.state.currentUser.phone);
            this.orders = data.orders || [];
            this.renderUserPanel(this.store.state);
        } catch (error) {
            console.error('Failed to load orders:', error);
            this.orders = [];
        }
    }

    renderUserPanel(state) {
        if (!this.container) return;

        const user = state.currentUser;
        if (!user) return;

        const ordersHtml = (this.orders || []).map(order => `
            <div class="order-card">
                <div>
                    <div class="order-number">#${order.id}</div>
                    <div class="order-date">Время готовности<br>${order.date}</div>
                    <div class="order-status">${order.status || 'Завершен'}</div>
                </div>
                <div>
                    <div class="order-address-title">Адрес кафе</div>
                    <div class="order-address">${order.address}</div>
                </div>
                <div>
                    <div class="order-price">${order.total} ₽</div>
                    <div class="order-payment">${order.payment}</div>
                </div>
            </div>
        `).join('');

        this.container.innerHTML = `
            <div class="modal-content user-panel-modal">
                <span class="close" id="closeUserPanel">&times;</span>
                <div class="user-header">
                    <h2>Привет, <span id="userName">${user.name || 'Пользователь'}</span></h2>
                    <p>Телефон: <span id="userPhone">${user.phone}</span></p>
                </div>
                <div class="user-info-card">
                    <div class="user-info-item">
                        <span class="info-label">Номер пользователя</span>
                        <strong id="userId">#${String(user.id || 1).padStart(4, '0')}</strong>
                    </div>
                </div>
                <div class="orders-title">
                    <h3>История заказов</h3>
                </div>
                <div id="orderHistory" class="order-history">
                    ${ordersHtml || '<p>У вас пока нет заказов</p>'}
                </div>
            </div>
        `;

        // Добавляем обработчик закрытия
        const closeBtn = this.container.querySelector('#closeUserPanel');
        if (closeBtn) {
            closeBtn.onclick = () => this.container.style.display = 'none';
        }
    }
}