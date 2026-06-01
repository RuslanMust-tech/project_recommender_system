// api.js - Абстракция для работы с API
const API_BASE_URL = "http://127.0.0.1:8001/api/v1";

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Пользователи
    async getUser(phone) {
        return this.request(`/user/${phone}`);
    }

    // Корзина
    async getCart(phone) {
        return this.request(`/cart/${phone}`);
    }

    async saveCart(phone, cart) {
        return this.request('/cart', {
            method: 'POST',
            body: JSON.stringify({ phone, cart })
        });
    }

    // Заказы
    async getOrders(phone) {
        return this.request(`/orders/${phone}`);
    }

    async createOrder(phone, order) {
        return this.request('/order', {
            method: 'POST',
            body: JSON.stringify({ phone, order })
        });
    }

    // Продукты
    async getProductsByCategory(category = null) {
        let endpoint = '/dishes/search/by_name';
        if (category) {
            endpoint += `?category=${encodeURIComponent(category)}`;
        }
        return this.request(endpoint);
    }

    async getProductsByCategory(name = null) {
        let endpoint = '/dishes/search/by_name';
        if (name) {
            endpoint += `?name=${encodeURIComponent(name)}`;
        }
        return this.request(endpoint);
    }

    async getUtensils() {
        return getProductsByCategory(category = "");
    }

    async getSauces() {
        return this.request('/sauces');
    }
}

const api = new ApiService();