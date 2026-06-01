// store.js - Управление состоянием
class Store {
    constructor() {
        this.state = {
            currentUser: null,
            cart: [],
            selectedUtensils: [],
            selectedSauces: [],
            products: [],
            categories: [],
            utensils: [],
            sauces: []
        };
        this.listeners = [];
        this.loadInitialData();
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    notify() {
        this.listeners.forEach(listener => listener(this.state));
    }

    setState(updates) {
        Object.assign(this.state, updates);
        this.notify();
        this.saveToLocalStorage();
    }

    async loadInitialData() {
        try {
            const [products, categories, utensils, sauces] = await Promise.all([
                api.getProducts(),
                api.getCategories(),
                api.getUtensils(),
                api.getSauces()
            ]);

            this.setState({
                products,
                categories,
                utensils,
                sauces
            });
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    async loadUser(phone) {
        try {
            const user = await api.getUser(phone);
            const cartData = await api.getCart(phone);

            this.setState({
                currentUser: user,
                cart: cartData.cart || []
            });

            return user;
        } catch (error) {
            throw error;
        }
    }

    async addToCart(product, quantity = 1) {
        const existingItem = this.state.cart.find(item => item.id === product.id);

        let newCart;
        if (existingItem) {
            newCart = this.state.cart.map(item =>
                item.id === product.id
                    ? { ...item, quantity: item.quantity + quantity }
                    : item
            );
        } else {
            newCart = [...this.state.cart, {
                ...product,
                quantity,
                addedAt: new Date()
            }];
        }

        this.setState({ cart: newCart });

        if (this.state.currentUser) {
            await api.saveCart(this.state.currentUser.phone, newCart);
        }
    }

    async updateCartItemQuantity(productId, delta) {
        const newCart = this.state.cart
            .map(item => {
                if (item.id === productId) {
                    const newQuantity = item.quantity + delta;
                    return newQuantity > 0 ? { ...item, quantity: newQuantity } : null;
                }
                return item;
            })
            .filter(item => item !== null);

        this.setState({ cart: newCart });

        if (this.state.currentUser) {
            await api.saveCart(this.state.currentUser.phone, newCart);
        }
    }

    async removeFromCart(productId) {
        const newCart = this.state.cart.filter(item => item.id !== productId);
        this.setState({ cart: newCart });

        if (this.state.currentUser) {
            await api.saveCart(this.state.currentUser.phone, newCart);
        }
    }

    async addUtensil(utensil) {
        if (!this.state.selectedUtensils.includes(utensil.id)) {
            this.setState({
                selectedUtensils: [...this.state.selectedUtensils, utensil.id]
            });
        }
    }

    async addSauce(sauce) {
        if (!this.state.selectedSauces.includes(sauce.id)) {
            this.setState({
                selectedSauces: [...this.state.selectedSauces, sauce.id]
            });
            // Добавляем соус в корзину как товар
            await this.addToCart({
                id: sauce.id,
                name: sauce.name,
                price: sauce.price,
                img: sauce.image,
                weight: '',
                type: 'sauce'
            }, 1);
        }
    }

    async createOrder(address = null) {
        if (!this.state.currentUser) {
            throw new Error('User not logged in');
        }

        const total = this.state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const order = {
            id: Date.now(),
            date: new Date().toLocaleString('ru-RU'),
            total,
            payment: 'Оплата через СБП',
            address: address || 'г. Уфа, ул. Степана Кувыкина, 27',
            items: this.state.cart.map(item => ({
                id: item.id,
                name: item.name,
                quantity: item.quantity,
                price: item.price
            })),
            utensils: this.state.selectedUtensils,
            sauces: this.state.selectedSauces
        };

        await api.createOrder(this.state.currentUser.phone, order);

        // Очищаем корзину
        this.setState({
            cart: [],
            selectedUtensils: [],
            selectedSauces: []
        });

        return order;
    }

    saveToLocalStorage() {
        const toSave = {
            currentUser: this.state.currentUser,
            selectedUtensils: this.state.selectedUtensils,
            selectedSauces: this.state.selectedSauces
        };
        localStorage.setItem('store_state', JSON.stringify(toSave));
    }

    loadFromLocalStorage() {
        const saved = localStorage.getItem('store_state');
        if (saved) {
            const data = JSON.parse(saved);
            this.setState({
                currentUser: data.currentUser,
                selectedUtensils: data.selectedUtensils || [],
                selectedSauces: data.selectedSauces || []
            });
        }
    }
}

const store = new Store();