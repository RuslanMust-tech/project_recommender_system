// store.js
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
            sauces: [],
            isLoading: false
        };
        this.listeners = [];

        // Загружаем начальные данные
        this.loadInitialData();
        this.loadFromLocalStorage();
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
        this.setState({ isLoading: true });

        try {
            const [products, categories, utensils, sauces] = await Promise.all([
                window.api.getProducts(),
                window.api.getCategories(),
                window.api.getUtensils(),
                window.api.getSauces()
            ]);

            this.setState({
                products: products || [],
                categories: categories || [],
                utensils: utensils || [],
                sauces: sauces || [],
                isLoading: false
            });

            console.log('Данные загружены:', {
                products: products.length,
                categories: categories.length
            });
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.setState({ isLoading: false });
        }
    }

    async loadUser(phone) {
        try {
            const user = await window.api.getUser(phone);
            const cartData = await window.api.getCart(phone);

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
        if (!product || product.id == null) {
            console.error('Cannot add product without id:', product);
            return;
        }

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
            await window.api.saveCart(this.state.currentUser.phone, newCart);
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
            await window.api.saveCart(this.state.currentUser.phone, newCart);
        }
    }

    async removeFromCart(productId) {
        const newCart = this.state.cart.filter(item => item.id !== productId);
        this.setState({ cart: newCart });

        if (this.state.currentUser) {
            await window.api.saveCart(this.state.currentUser.phone, newCart);
        }
    }

    async addUtensil(utensilId) {
        if (!this.state.selectedUtensils.includes(utensilId)) {
            this.setState({
                selectedUtensils: [...this.state.selectedUtensils, utensilId]
            });
        }
    }

    async addSauce(sauceId) {
        if (!this.state.selectedSauces.includes(sauceId)) {
            this.setState({
                selectedSauces: [...this.state.selectedSauces, sauceId]
            });

            const sauce = this.state.sauces.find(s => s.id === sauceId);
            if (sauce) {
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
    }

    async createOrder(address = null) {
        if (!this.state.currentUser) {
            throw new Error('User not logged in');
        }

        const total = this.state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const order = {
            user_id: this.state.user,
            total: total,
            items: this.state.cart.map(item => ({
                id: item.id,
                name: item.name,
                quantity: item.quantity,
                price: item.price
            })),
        };

        await window.api.createOrder(this.state.currentUser.phone, order);

        this.setState({
            cart: [],
            selectedUtensils: [],
            selectedSauces: []
        });

        return order;
    }

    getCartTotal() {
        return this.state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    }

    getCartItemsCount() {
        return this.state.cart.reduce((sum, item) => sum + item.quantity, 0);
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

window.store = new Store();
