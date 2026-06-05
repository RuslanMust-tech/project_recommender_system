// main.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Приложение запущено');

    const productsContainer = document.getElementById('productsGrid');
    const categoriesContainer = document.getElementById('categoryFilter');
    const cartContainer = document.getElementById('cart-items-container');
    const userPanelContainer = document.getElementById('userPanel');
    const mlRecommendationsContainer = document.getElementById('ml-recommendations-container');

    window.productsGrid = new window.ProductsGrid(productsContainer, window.store);
    window.cartComponent = new window.CartComponent(cartContainer, window.store);
    window.userPanel = new window.UserPanel(userPanelContainer, window.store);
    window.mlRecommendationComponent = new window.MLRecommendationComponent(mlRecommendationsContainer, window.store);

    new window.CategoriesFilter(categoriesContainer, window.store, (category) => {
        if (window.productsGrid) {
            window.productsGrid.filterByCategory(category);
        }
    });

    setupEventHandlers();
});

function setupEventHandlers() {
    const showMenuBtn = document.getElementById('showMenuBtn');
    if (showMenuBtn) {
        showMenuBtn.addEventListener('click', () => {
            const productsGrid = document.getElementById('productsGrid');
            const categoryFilter = document.getElementById('categoryFilter');

            if (window.productsGrid) {
                window.productsGrid.currentCategory = null;
                window.productsGrid.renderProducts(window.store.state.products);
            }

            if (categoryFilter) {
                categoryFilter.querySelectorAll('.category').forEach(c => c.classList.remove('active'));
            }

            if (productsGrid) productsGrid.style.display = 'grid';
            if (categoryFilter) categoryFilter.style.display = 'flex';
            if (productsGrid) productsGrid.scrollIntoView({ behavior: 'smooth' });
        });
    }

    const openLoginBtn = document.querySelector('.login');
    if (openLoginBtn) {
        openLoginBtn.onclick = () => {
            const loginModal = document.getElementById('loginModal');
            if (loginModal) loginModal.style.display = 'flex';
        };
    }

    const loginBtn = document.getElementById('loginBtn');
    const phoneInput = document.getElementById('phone');
    const loginModal = document.getElementById('loginModal');
    if (loginBtn && phoneInput) {
        loginBtn.onclick = async () => {
            const phone = phoneInput.value.replace(/\D/g, '');
            if (!phone) return alert('Введите номер');
            try {
                await window.store.loadUser(phone);
                if (loginModal) loginModal.style.display = 'none';
                alert(`Добро пожаловать!`);
            } catch (error) {
                alert('Ошибка входа');
            }
        };
    }

    const cartBtn = document.querySelector('.cart');
    const cartModal = document.getElementById('cartModal');
    if (cartBtn && cartModal) {
        cartBtn.onclick = () => cartModal.style.display = 'flex';
    }

    const userPanelBtn = document.querySelector('.user-panel-btn');
    if (userPanelBtn && window.userPanel) {
        userPanelBtn.onclick = () => window.userPanel.show();
    }

    const modals = ['loginModal', 'cartModal', 'userPanel'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            const closeBtn = modal.querySelector('.close');
            if (closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
            modal.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };
        }
    });
}