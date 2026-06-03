// api.js
const API_BASE_URL = "http://127.0.0.1:8001/api/v1";

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
        this.imagesPath = "/static/images/"; // Папка с картинками .webp
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

    // Формируем путь к картинке по названию блюда
    getImageUrl(productName) {
        // Очищаем имя для использования в URL
        const cleanName = productName
            .replace(/[<>:"/\\|?*]/g, '')
            .trim();
        return `${this.imagesPath}${encodeURIComponent(cleanName)}.webp`;
    }

    // Форматируем вес из граммов в читаемый вид
    formatWeight(weightGram) {
        if (!weightGram) return '';
        if (weightGram >= 1000) {
            return `${weightGram / 1000} кг`;
        }
        return `${weightGram} г`;
    }

    // Форматируем количество штук
    formatPieces(pieces) {
        if (!pieces) return '';
        if (pieces === 1) return `${pieces} шт`;
        return `${pieces} шт`;
    }

    // Преобразуем продукт из БД в формат для фронта
    transformProduct(dbProduct) {
        // Формируем строку веса/количества
        let weightText = '';
        if (dbProduct.pieces) {
            weightText = this.formatPieces(dbProduct.pieces);
        } else if (dbProduct.weight_g) {
            weightText = this.formatWeight(dbProduct.weight_g);
        }

        // Формируем лейблы (можно добавить логику для акций)
        const labels = [];

        // Пример: если калорийность низкая
        if (dbProduct.calories_kcal && dbProduct.calories_kcal < 300) {
            labels.push({ type: 'choice', text: 'Диетическое' });
        }

        // Пример: если белка много
        if (dbProduct.proteins_g && dbProduct.proteins_g > 20) {
            labels.push({ type: 'hit', text: 'Много белка' });
        }

        return {
            id: dbProduct.id,
            name: dbProduct.name,
            category: dbProduct.category,
            price: dbProduct.price_rub,
            weight: weightText,
            weight_g: dbProduct.weight_g,
            pieces: dbProduct.pieces,
            composition: dbProduct.composition,
            proteins: dbProduct.proteins_g,
            fats: dbProduct.fats_g,
            carbs: dbProduct.carbs_g,
            calories: dbProduct.calories_kcal,
            image: this.getImageUrl(dbProduct.name),
            labels: labels,
            // Для обратной совместимости
            img: this.getImageUrl(dbProduct.name)
        };
    }

    // Получить все продукты
    async getProducts(category = null) {
        let endpoint = '/dishes';
        if (category) {
            endpoint += `?category=${encodeURIComponent(category)}`;
        }
        const products = await this.request(endpoint);

        // Трансформируем каждый продукт
        return products.map(product => this.transformProduct(product));
    }

    // Получить все категории с количеством продуктов
    async getCategories() {
        const products = await this.getProducts();
        const categoriesMap = new Map();

        products.forEach(product => {
            if (!categoriesMap.has(product.category)) {
                categoriesMap.set(product.category, 0);
            }
            categoriesMap.set(product.category, categoriesMap.get(product.category) + 1);
        });

        return Array.from(categoriesMap.entries()).map(([name, count]) => ({
            name: name,
            count: count
        }));
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
        return this.request(`/user/${phone}/orders`);
    }

    async createOrder(phone, order) {
        return this.request('/orders', {
            method: 'POST',
            body: JSON.stringify({ phone, order })
        });
    }

    async getCartRecommendations(itemIds, phone = null) {
        const params = new URLSearchParams();
        itemIds.forEach(id => params.append('item_ids', id));
        if (phone) params.set('phone', phone);
        return this.request(`/recommendations/cart?${params.toString()}`);
    }

    // Соусы и приборы (если есть в БД)
    async getUtensils() {
        // Если есть таблица с приборами
        try {
            return await this.request('/utensils');
        } catch {
            // Возвращаем заглушку
            return [
                { id: 1, name: "Палочки, салфетки, зубочистка", price: 0, image: "/static/img/utensils.webp" },
                { id: 2, name: "Вилка", price: 0, image: "/static/img/fork.png" },
                { id: 3, name: "Ложка", price: 0, image: "/static/img/spoon.png" }
            ];
        }
    }

    async getSauces() {
        // Если есть таблица с соусами
        try {
            return await this.request('/sauces');
        } catch {
            // Возвращаем заглушку
            return [
                { id: 1, name: "Соевый соус", price: 0, image: "/static/img/soy.png" },
                { id: 2, name: "Васаби", price: 0, image: "/static/img/wasabi.png" },
                { id: 3, name: "Имбирь", price: 0, image: "/static/img/ginger.png" },
                { id: 4, name: "Майонезный соус", price: 0, image: "/static/img/mayo.png" }
            ];
        }
    }

    async getMLRecommendations(cartItemNames, phone = null) {
        if (!cartItemNames || cartItemNames.length === 0) {
            return [];
        }
        
        try {
            return await this.request('/ml/recommendations/ml', {
                method: 'POST',
                body: JSON.stringify({
                    phone: phone,
                    current_cart: cartItemNames,
                    limit: 10
                })
            });
        } catch (error) {
            console.warn('ML recommendations unavailable:', error);
            return null;
        }
    }
}

// Создаем глобальный экземпляр
window.api = new ApiService();
