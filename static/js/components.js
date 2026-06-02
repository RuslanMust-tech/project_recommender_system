// components.js
class ProductsGrid {
    constructor(container, store) {
        this.container = container;
        this.store = store;
        this.currentCategory = null;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            if (state.products && state.products.length > 0) {
                this.renderProducts(state.products);
            }
        });
    }

    renderProducts(products) {
        if (!this.container) return;

        let filteredProducts = products;
        if (this.currentCategory) {
            filteredProducts = products.filter(p => p.category === this.currentCategory);
        }

        if (filteredProducts.length === 0) {
            this.container.innerHTML = '<div class="no-products">Нет товаров в этой категории</div>';
            return;
        }

        this.container.innerHTML = filteredProducts.map(product => `
            <div class="product" data-category="${product.category}" data-product-id="${product.id}">
                <img src="${product.image}" 
                     alt="${product.name}" 
                     loading="lazy" 
                     onerror="this.src='/static/img/placeholder.jpg'">
                <div class="labels">
                    ${product.labels.map(label => `
                        <span class="label ${label.type}">${label.text}</span>
                    `).join('')}
                </div>
                <strong>${product.name}</strong>
                <p>${product.weight}</p>
                ${product.calories ? `<p class="calories">${product.calories} ккал</p>` : ''}
                <div class="product-price">${product.price} ₽</div>
                <button onclick="window.productsGrid.addToCart(${product.id})">
                    В корзину ${product.price} ₽ →
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
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

class CategoriesFilter {
    constructor(container, store, onCategorySelect) {
        this.container = container;
        this.store = store;
        this.onCategorySelect = onCategorySelect;
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            if (state.categories && state.categories.length > 0) {
                this.renderCategories(state.categories);
            }
        });
    }

    renderCategories(categories) {
        if (!this.container) return;

        this.container.innerHTML = categories.map(category => `
            <div class="category" data-cat="${category.name}">
                ${category.name}
                <span class="category-count">(${category.count})</span>
            </div>
        `).join('');

        this.container.querySelectorAll('.category').forEach(el => {
            el.addEventListener('click', () => {
                const category = el.dataset.cat;
                this.onCategorySelect(category);

                this.container.querySelectorAll('.category').forEach(c => c.classList.remove('active'));
                el.classList.add('active');
            });
        });
    }
}

class CartComponent {
    constructor(container, store) {
        this.container = container;
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
        const total = this.store.getCartTotal();

        const cartItemsHtml = cart.length === 0
            ? '<li class="empty-cart">Корзина пуста</li>'
            : cart.map(item => `
                <li class="cart-item" data-item-id="${item.id}">
                    ${item.img ? `<img src="${item.img}" alt="${item.name}" class="cart-img" onerror="this.src='/static/img/placeholder.jpg'">` : ''}
                    <div class="cart-item-info">
                        <span class="cart-item-name">${item.name}</span>
                        <span class="cart-item-weight">${item.weight || ''}</span>
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

        const utensilsHtml = (utensils || []).map(utensil => `
            <div class="utensil-item" data-utensil-id="${utensil.id}">
                <img src="${utensil.image}" alt="${utensil.name}" onerror="this.src='/static/img/placeholder.jpg'">
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

        const saucesHtml = (sauces || []).map(sauce => `
            <div class="sauce-item" data-sauce-id="${sauce.id}">
                <img src="${sauce.image}" alt="${sauce.name}" onerror="this.src='/static/img/placeholder.jpg'">
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
            <ul class="cart-items">${cartItemsHtml}</ul>
            
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
                <strong class="cart-total">${total} ₽</strong>
                <button id="checkoutBtn" class="checkout-btn">Оформить заказ</button>
            </div>
        `;

        const checkoutBtn = this.container.querySelector('#checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.onclick = () => this.checkout();
        }
    }

    updateCartCount(cart) {
        const totalItems = this.store.getCartItemsCount();
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
        await this.store.addUtensil(utensilId);
    }

    async addSauce(sauceId) {
        await this.store.addSauce(sauceId);
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
            const cartModal = document.getElementById('cartModal');
            if (cartModal) cartModal.style.display = 'none';
        } catch (error) {
            alert('Ошибка при оформлении заказа: ' + error.message);
        }
    }
}

class UserPanel {
    constructor(container, store) {
        this.container = container;
        this.store = store;
        this.orders = [];
        this.init();
    }

    init() {
        this.store.subscribe((state) => {
            if (this.container && this.container.style.display === 'flex') {
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
        if (this.container) {
            this.container.style.display = 'flex';
        }
    }

    async loadOrders() {
        if (!this.store.state.currentUser) return;

        try {
            const data = await window.api.getOrders(this.store.state.currentUser.phone);
            this.orders = data.orders || [];
        } catch (error) {
            console.error('Failed to load orders:', error);
            this.orders = [];
        }
    }

    renderUserPanel(state) {
        if (!this.container) return;

        const user = state.currentUser;
        if (!user) return;

        const ordersHtml = this.orders.map(order => `
            <div class="order-card">
                <div>
                    <div class="order-number">#${order.id}</div>
                    <div class="order-date">${order.date}</div>
                    <div class="order-status">${order.status || 'Завершен'}</div>
                </div>
                <div>
                    <div class="order-address-title">Адрес доставки</div>
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
                    <h2>Привет, ${user.name || 'Пользователь'}</h2>
                    <p>Телефон: ${user.phone}</p>
                </div>
                <div class="user-info-card">
                    <div class="user-info-item">
                        <span class="info-label">Номер пользователя</span>
                        <strong>#${String(user.id || 1).padStart(4, '0')}</strong>
                    </div>
                </div>
                <div class="orders-title">
                    <h3>История заказов (${this.orders.length})</h3>
                </div>
                <div class="order-history">
                    ${ordersHtml || '<p>У вас пока нет заказов</p>'}
                </div>
            </div>
        `;

        const closeBtn = this.container.querySelector('#closeUserPanel');
        if (closeBtn) {
            closeBtn.onclick = () => {
                if (this.container) this.container.style.display = 'none';
            };
        }
    }
}

window.ProductsGrid = ProductsGrid;
window.CategoriesFilter = CategoriesFilter;
window.CartComponent = CartComponent;
window.UserPanel = UserPanel;