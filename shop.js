// PipeDrill Pro - Complete Shopping and Service System
class PipeDrillSystem {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('pipeDrillCart')) || [];
        this.products = [];
        this.services = [];
        this.orders = [];
        this.serviceRequests = [];
        
        this.init();
    }

    async init() {
        await this.loadProducts();
        await this.loadServices();
        await this.loadOrders();
        await this.loadServiceRequests();
        
        this.setupEventListeners();
        this.updateCartDisplay();
        this.updateCartCount();
    }

    async loadProducts() {
        try {
            const response = await fetch('/api/products');
            const data = await response.json();
            if (data.success) {
                this.products = data.products;
                this.displayProducts(this.products);
            }
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    async loadServices() {
        try {
            const response = await fetch('/api/services');
            const data = await response.json();
            if (data.success) {
                this.services = data.services;
                this.displayServices(this.services);
            }
        } catch (error) {
            console.error('Error loading services:', error);
        }
    }

    async loadOrders() {
        try {
            const response = await fetch('/api/product-orders');
            const data = await response.json();
            if (data.success) {
                this.orders = data.orders;
            }
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    async loadServiceRequests() {
        try {
            const response = await fetch('/api/service-requests');
            const data = await response.json();
            if (data.success) {
                this.serviceRequests = data.requests;
            }
        } catch (error) {
            console.error('Error loading service requests:', error);
        }
    }

    displayProducts(products) {
        const container = document.getElementById('productsContainer');
        if (!container) return;

        container.innerHTML = products.map(product => `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-image">
                    <i class="fas fa-${this.getProductIcon(product.category)} fa-3x"></i>
                </div>
                <h3>${product.name}</h3>
                <p class="product-description">${product.description}</p>
                
                <div class="product-specs">
                    ${Object.entries(product.specs || {}).map(([key, value]) => `
                        <div class="spec-item">
                            <strong>${this.formatSpecKey(key)}:</strong> ${value}
                        </div>
                    `).join('')}
                </div>

                <div class="product-features">
                    ${product.features.map(feature => 
                        `<span class="feature-tag">${feature}</span>`
                    ).join('')}
                </div>

                <div class="product-pricing">
                    <span class="price">$${product.price.toFixed(2)}/${product.unit}</span>
                    <span class="stock">In Stock: ${product.stock}</span>
                </div>

                <button class="btn btn-primary" onclick="pipeSystem.addToCart(${product.id})">
                    <i class="fas fa-cart-plus"></i> Add to Cart
                </button>
            </div>
        `).join('');
    }

    displayServices(services) {
        const container = document.getElementById('servicesContainer');
        if (!container) return;

        container.innerHTML = services.map(service => `
            <div class="service-card" data-service-id="${service.id}">
                <h3>${service.name}</h3>
                <p class="service-description">${service.description}</p>
                
                <div class="service-pricing">
                    <span class="price">$${service.hourly_rate.toFixed(2)}/hour</span>
                    <span class="min-hours">Minimum: ${service.min_hours} hours</span>
                </div>

                <div class="service-features">
                    ${service.features.map(feature => 
                        `<span class="feature-tag">${feature}</span>`
                    ).join('')}
                </div>

                <div class="service-materials">
                    <strong>Materials:</strong> ${service.materials.join(', ')}
                </div>

                <button class="btn btn-outline" onclick="pipeSystem.bookService(${service.id})">
                    <i class="fas fa-calendar-check"></i> Book Service
                </button>
            </div>
        `).join('');
    }

    getProductIcon(category) {
        const icons = {
            'pipes': 'pipe',
            'machines': 'cogs',
            'tools': 'tools',
            'accessories': 'toolbox'
        };
        return icons[category] || 'box';
    }

    formatSpecKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    addToCart(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;

        if (product.stock <= 0) {
            this.showNotification('Product out of stock', 'error');
            return;
        }

        const existingItem = this.cart.find(item => item.id === productId);
        if (existingItem) {
            if (existingItem.quantity < product.stock) {
                existingItem.quantity++;
            } else {
                this.showNotification('Maximum stock reached for this item', 'error');
                return;
            }
        } else {
            this.cart.push({
                ...product,
                quantity: 1,
                itemType: 'product'
            });
        }

        this.saveCart();
        this.updateCartDisplay();
        this.updateCartCount();
        this.showNotification(`${product.name} added to cart`);
    }

    removeFromCart(itemId) {
        this.cart = this.cart.filter(item => item.id !== itemId);
        this.saveCart();
        this.updateCartDisplay();
        this.updateCartCount();
    }

    updateQuantity(itemId, change) {
        const item = this.cart.find(item => item.id === itemId);
        if (!item) return;

        const newQuantity = item.quantity + change;
        
        if (newQuantity <= 0) {
            this.removeFromCart(itemId);
            return;
        }
        
        if (item.itemType === 'product') {
            const product = this.products.find(p => p.id === itemId);
            if (newQuantity > product.stock) {
                this.showNotification(`Only ${product.stock} items available in stock`, 'error');
                return;
            }
        }
        
        item.quantity = newQuantity;
        this.saveCart();
        this.updateCartDisplay();
    }

    updateCartDisplay() {
        const container = document.getElementById('cartContainer');
        const summary = document.getElementById('cartSummary');
        
        if (!container || !summary) return;

        if (this.cart.length === 0) {
            container.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart fa-3x"></i>
                    <h3>Your cart is empty</h3>
                    <p>Add some products or services to get started</p>
                </div>
            `;
            summary.innerHTML = '<p class="total">Total: $0.00</p>';
            return;
        }

        let subtotal = 0;
        container.innerHTML = this.cart.map(item => {
            let itemTotal = 0;
            
            if (item.itemType === 'product') {
                itemTotal = item.price * item.quantity;
            } else if (item.itemType === 'service') {
                itemTotal = item.hourly_rate * item.estimated_hours;
            }
            
            subtotal += itemTotal;

            return `
                <div class="cart-item">
                    <div class="item-info">
                        <h4>${item.name}</h4>
                        <p>${item.itemType === 'product' ? 
                            `$${item.price}/${item.unit}` : 
                            `Service (${item.estimated_hours} hours)`}
                        </p>
                    </div>
                    <div class="quantity-controls">
                        ${item.itemType === 'product' ? `
                            <button onclick="pipeSystem.updateQuantity(${item.id}, -1)">-</button>
                            <span>${item.quantity}</span>
                            <button onclick="pipeSystem.updateQuantity(${item.id}, 1)">+</button>
                        ` : ''}
                    </div>
                    <div class="item-total">$${itemTotal.toFixed(2)}</div>
                    <button class="btn btn-danger" onclick="pipeSystem.removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');

        const tax = subtotal * 0.08; // 8% tax
        const total = subtotal + tax;

        summary.innerHTML = `
            <div class="summary-item">
                <span>Subtotal:</span>
                <span>$${subtotal.toFixed(2)}</span>
            </div>
            <div class="summary-item">
                <span>Tax (8%):</span>
                <span>$${tax.toFixed(2)}</span>
            </div>
            <div class="summary-item total">
                <span>Total:</span>
                <span>$${total.toFixed(2)}</span>
            </div>
            <button class="btn btn-success checkout-btn" onclick="pipeSystem.checkout()">
                <i class="fas fa-credit-card"></i> Proceed to Checkout
            </button>
        `;
    }

    updateCartCount() {
        const count = this.cart.reduce((total, item) => total + item.quantity, 0);
        const countElement = document.getElementById('cartCount');
        if (countElement) {
            countElement.textContent = count;
        }
    }

    async checkout() {
        if (this.cart.length === 0) {
            this.showNotification('Your cart is empty!', 'error');
            return;
        }

        try {
            const response = await fetch('/api/place-order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    items: this.cart,
                    subtotal: this.cart.reduce((sum, item) => {
                        if (item.itemType === 'product') {
                            return sum + (item.price * item.quantity);
                        } else {
                            return sum + (item.hourly_rate * item.estimated_hours);
                        }
                    }, 0),
                    tax: this.cart.reduce((sum, item) => {
                        if (item.itemType === 'product') {
                            return sum + (item.price * item.quantity);
                        } else {
                            return sum + (item.hourly_rate * item.estimated_hours);
                        }
                    }, 0) * 0.08,
                    total: this.cart.reduce((sum, item) => {
                        if (item.itemType === 'product') {
                            return sum + (item.price * item.quantity);
                        } else {
                            return sum + (item.hourly_rate * item.estimated_hours);
                        }
                    }, 0) * 1.08
                })
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Order placed successfully!', 'success');
                this.cart = [];
                this.saveCart();
                this.updateCartDisplay();
                this.updateCartCount();
                
                // Reload orders
                await this.loadOrders();
            } else {
                this.showNotification('Error placing order: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Network error. Please try again.', 'error');
        }
    }

    bookService(serviceId) {
        const service = this.services.find(s => s.id === serviceId);
        if (!service) return;

        // Pre-fill service booking form
        document.getElementById('serviceType').value = service.name.toLowerCase().replace(/\s+/g, '-');
        this.showNotification(`Ready to book: ${service.name}`);
        
        // Switch to services tab
        this.switchTab('services');
    }

    switchTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
        
        document.getElementById(tabName).classList.add('active');
        document.querySelector(`.nav-tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
    }

    setupEventListeners() {
        // Product search
        const searchInput = document.getElementById('productSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                const filtered = this.products.filter(product =>
                    product.name.toLowerCase().includes(term) ||
                    product.description.toLowerCase().includes(term) ||
                    product.category.toLowerCase().includes(term)
                );
                this.displayProducts(filtered);
            });
        }

        // Service request form
        const serviceForm = document.getElementById('serviceForm');
        if (serviceForm) {
            serviceForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitServiceRequest();
            });
        }
    }

    async submitServiceRequest() {
        const formData = {
            service_type: document.getElementById('serviceType').value,
            pipe_material: document.getElementById('pipeMaterial').value,
            pipe_diameter: parseFloat(document.getElementById('pipeDiameter').value),
            estimated_hours: parseInt(document.getElementById('estimatedHours').value),
            description: document.getElementById('projectDescription').value,
            contact_name: document.getElementById('contactName').value,
            contact_email: document.getElementById('contactEmail').value,
            contact_phone: document.getElementById('contactPhone').value
        };

        try {
            const response = await fetch('/api/service-request', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Service request submitted successfully!', 'success');
                document.getElementById('serviceForm').reset();
                
                // Add to cart as service item
                const service = this.services.find(s => 
                    s.name.toLowerCase().replace(/\s+/g, '-') === formData.service_type
                );
                
                if (service) {
                    this.cart.push({
                        ...service,
                        ...formData,
                        itemType: 'service',
                        id: Date.now() // Temporary ID for cart
                    });
                    this.saveCart();
                    this.updateCartCount();
                }
                
            } else {
                this.showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Network error. Please try again.', 'error');
        }
    }

    showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    saveCart() {
        localStorage.setItem('pipeDrillCart', JSON.stringify(this.cart));
    }
}

// Initialize the system when page loads
let pipeSystem;
document.addEventListener('DOMContentLoaded', () => {
    pipeSystem = new PipeDrillSystem();
});

// Global functions for HTML onclick handlers
function switchTab(tabName) {
    if (pipeSystem) {
        pipeSystem.switchTab(tabName);
    }
}

function addToCart(productId) {
    if (pipeSystem) {
        pipeSystem.addToCart(productId);
    }
}

function checkout() {
    if (pipeSystem) {
        pipeSystem.checkout();
    }
}