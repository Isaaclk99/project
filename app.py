from flask import Flask, request, jsonify, send_from_directory, render_template_string
import json
import os
from datetime import datetime
from decimal import Decimal
import base64

app = Flask(__name__)

# File paths
REQUESTS_FILE = 'data/service_requests.json'
PRODUCTS_FILE = 'data/products.json'
ORDERS_FILE = 'data/orders.json'
UPLOAD_FOLDER = 'static/images'
os.makedirs('data', exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize sample data with actual image URLs
def init_data():
    """Initialize with sample data"""
    sample_products = [
        {
            "id": 1, "name": "Stainless Steel Pipe 2-inch", "category": "pipes",
            "description": "304 Stainless steel pipe, 2-inch diameter, schedule 40",
            "price": 12.50, "unit": "foot", "stock": 150, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "specs": {"material": "304 SS", "diameter": "2 inch", "wall_thickness": "0.154 inch"},
            "features": ["Corrosion resistant", "Food grade", "Weldable"]
        },
        {
            "id": 2, "name": "Carbon Steel Pipe 3-inch", "category": "pipes",
            "description": "ASTM A106 carbon steel pipe, 3-inch diameter, schedule 80",
            "price": 8.75, "unit": "foot", "stock": 200, 
            "image": "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?w=400",
            "specs": {"material": "A106 Gr B", "diameter": "3 inch", "wall_thickness": "0.216 inch"},
            "features": ["High strength", "Cost effective", "Versatile"]
        },
        {
            "id": 3, "name": "Drilling Machine Industrial", "category": "machines",
            "description": "Heavy-duty pipe drilling machine with precision guides",
            "price": 4500.00, "unit": "unit", "stock": 15, 
            "image": "https://images.unsplash.com/photo-1581094794322-3a6e3c8aa330?w=400",
            "specs": {"max_capacity": "12 inch", "power": "5HP", "accuracy": "±0.001 inch"},
            "features": ["Industrial grade", "Precision drilling", "Safety features"]
        },
        {
            "id": 4, "name": "Carbide Drill Bit Set", "category": "tools",
            "description": "Professional carbide drill bits for steel pipes",
            "price": 189.99, "unit": "set", "stock": 50, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "specs": {"sizes": "1/4\" to 2\"", "material": "Carbide", "shank": "3/8 inch"},
            "features": ["Long lasting", "Precision ground", "Heat resistant"]
        },
        {
            "id": 5, "name": "Pipe Clamping System", "category": "accessories",
            "description": "Professional pipe clamping system for secure drilling",
            "price": 345.00, "unit": "set", "stock": 30, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "specs": {"capacity": "1-8 inch", "material": "Steel", "adjustable": "Yes"},
            "features": ["Secure holding", "Quick release", "Heavy duty"]
        },
        {
            "id": 6, "name": "Coolant System", "category": "accessories",
            "description": "Automatic coolant system for pipe drilling operations",
            "price": 620.00, "unit": "unit", "stock": 20, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "specs": {"capacity": "5 gallons", "flow_rate": "2 GPM", "auto_control": "Yes"},
            "features": ["Temperature control", "Auto refill", "Filtration system"]
        }
    ]

    sample_services = [
        {
            "id": 1, "name": "Precision Pipe Drilling", "category": "drilling",
            "description": "Professional pipe drilling service with precision accuracy",
            "hourly_rate": 85.00, "min_hours": 2, 
            "image": "https://images.unsplash.com/photo-1581094794322-3a6e3c8aa330?w=400",
            "features": ["Laser guided", "CAD/CAM support", "Quality certification"],
            "materials": ["Stainless Steel", "Carbon Steel", "Aluminum", "Copper"]
        },
        {
            "id": 2, "name": "Pipe Threading Service", "category": "threading", 
            "description": "High-quality pipe threading for perfect connections",
            "hourly_rate": 75.00, "min_hours": 1, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "features": ["NPT standards", "Precision threads", "Leak testing"],
            "materials": ["Steel", "Brass", "Stainless Steel"]
        },
        {
            "id": 3, "name": "Custom Pipe Fabrication", "category": "fabrication",
            "description": "Custom pipe cutting, bending, and fabrication services",
            "hourly_rate": 95.00, "min_hours": 3, 
            "image": "https://images.unsplash.com/photo-1581094794322-3a6e3c8aa330?w=400",
            "features": ["CAD design", "Prototype support", "Volume discounts"],
            "materials": ["All metals", "Plastics", "Composites"]
        },
        {
            "id": 4, "name": "Emergency Repair Service", "category": "repair",
            "description": "24/7 emergency pipe drilling and repair services",
            "hourly_rate": 120.00, "min_hours": 1, 
            "image": "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400",
            "features": ["24/7 availability", "Rapid response", "Mobile service"],
            "materials": ["All materials", "On-site service"]
        }
    ]

    # Create files if they don't exist
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump({"products": sample_products, "services": sample_services}, f, indent=2)
    
    if not os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)

def load_data(filename):
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_data(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Main HTML Page with updated image handling
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Tuu Tuu Family Pipe & Tube Well Services </title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --accent: #e74c3c;
            --success: #27ae60;
            --warning: #f39c12;
            --light: #ecf0f1;
            --dark: #2c3e50;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; }
        
        .header { 
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white; padding: 2rem 0; text-align: center;
        }
        
        .nav-tabs { 
            display: flex; background: var(--dark); justify-content: center;
            position: sticky; top: 0; z-index: 100; flex-wrap: wrap;
        }
        .nav-tab { 
            padding: 1rem 2rem; color: white; cursor: pointer; border: none;
            background: none; transition: all 0.3s; font-weight: 500;
        }
        .nav-tab:hover { background: rgba(255,255,255,0.1); }
        .nav-tab.active { background: var(--secondary); }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .tab-content { display: none; animation: fadeIn 0.5s; }
        .tab-content.active { display: block; }
        
        .card { 
            background: white; padding: 2rem; margin: 1rem 0; 
            border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        
        .grid { 
            display: grid; gap: 2rem; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .product-card, .service-card {
            border: 1px solid #e0e0e0; border-radius: 10px; padding: 1.5rem;
            transition: all 0.3s; background: white; display: flex; flex-direction: column;
        }
        .product-card:hover, .service-card:hover {
            transform: translateY(-5px); box-shadow: 0 5px 25px rgba(0,0,0,0.15);
        }
        
        .product-image {
            width: 100%; height: 200px; object-fit: cover; border-radius: 8px;
            background: #f8f9fa; margin-bottom: 1rem; overflow: hidden;
        }
        
        .product-image img {
            width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s;
        }
        
        .product-card:hover .product-image img {
            transform: scale(1.05);
        }
        
        .image-placeholder {
            width: 100%; height: 100%; display: flex; align-items: center; 
            justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; font-size: 3rem;
        }
        
        .price { color: var(--accent); font-size: 1.4rem; font-weight: bold; margin: 10px 0; }
        .rating { color: var(--warning); }
        
        .btn {
            padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer;
            font-size: 1rem; transition: all 0.3s; margin: 5px; font-weight: 600;
        }
        .btn-primary { background: var(--secondary); color: white; }
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--accent); color: white; }
        .btn-outline { background: transparent; border: 2px solid var(--secondary); color: var(--secondary); }
        
        .cart-item { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 1rem; border-bottom: 1px solid #eee;
        }
        .quantity-controls { display: flex; align-items: center; gap: 10px; }
        
        .form-group { margin: 1rem 0; }
        .form-control { 
            width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px;
            font-size: 1rem; transition: border-color 0.3s;
        }
        .form-control:focus { outline: none; border-color: var(--secondary); }
        
        .feature-tag {
            background: var(--light); padding: 4px 8px; border-radius: 4px;
            font-size: 0.8rem; margin: 2px; display: inline-block;
        }
        
        .search-container {
            position: relative;
            margin-bottom: 1rem;
        }
        
        .search-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #7f8c8d;
        }
        
        .order-card {
            border-left: 4px solid var(--secondary);
            margin-bottom: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .order-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .status-pending { background: #fff3cd; color: #856404; }
        .status-completed { background: #d4edda; color: #155724; }
        .status-in-progress { background: #cce5ff; color: #004085; }
        
        .image-upload-container {
            margin: 1rem 0;
            padding: 1rem;
            border: 2px dashed #ddd;
            border-radius: 8px;
            text-align: center;
        }
        
        .image-preview {
            max-width: 200px;
            max-height: 200px;
            margin: 1rem auto;
            display: none;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .notification {
            position: fixed; top: 20px; right: 20px; padding: 1rem 2rem;
            border-radius: 5px; color: white; z-index: 1000; animation: slideIn 0.3s;
        }
        .notification.success { background: var(--success); }
        .notification.error { background: var(--accent); }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .nav-tabs { flex-direction: column; }
            .nav-tab { width: 100%; text-align: center; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-tools"></i> PipeDrill Pro</h1>
        <p>Tuu Tuu Family Pipe & Tube Wall Drilling Services</p>
    </div>
    
    <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('home')"><i class="fas fa-home"></i> Home</button>
        <button class="nav-tab" onclick="switchTab('services')"><i class="fas fa-concierge-bell"></i> Drilling Services</button>
        <button class="nav-tab" onclick="switchTab('products')"><i class="fas fa-shopping-cart"></i> Pipe Supplies</button>
        <button class="nav-tab" onclick="switchTab('cart')"><i class="fas fa-shopping-bag"></i> Cart (<span id="cartCount">0</span>)</button>
        <button class="nav-tab" onclick="switchTab('orders')"><i class="fas fa-clipboard-list"></i> My Orders</button>
        <button class="nav-tab" onclick="switchTab('admin')"><i class="fas fa-cog"></i> Admin</button>
    </div>
    
    <div class="container">
        <!-- Home Tab -->
        <div id="home" class="tab-content active">
            <div class="card">
                <h2>Welcome to PipeDrill Pro</h2>
                <p>Your one-stop solution for professional pipe drilling services and industrial pipe supplies.</p>
                
                <div class="grid" style="margin-top: 2rem;">
                    <div class="card">
                        <h3><i class="fas fa-hammer"></i> Drilling Services</h3>
                        <p>Professional pipe drilling, threading, and fabrication services</p>
                        <button class="btn btn-primary" onclick="switchTab('services')">Book Service</button>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-box-open"></i> Pipe Supplies</h3>
                        <p>High-quality pipes, tools, and drilling equipment</p>
                        <button class="btn btn-primary" onclick="switchTab('products')">Shop Now</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Services Tab -->
        <div id="services" class="tab-content">
            <h2>Professional Drilling Services</h2>
            <div class="card">
                <h3>Book a Service</h3>
                <form id="serviceForm" class="grid-2">
                    <div class="form-group">
                        <label>Service Type</label>
                        <select id="serviceType" class="form-control" required>
                            <option value="">Select Service</option>
                            <option value="precision-drilling">Precision Drilling</option>
                            <option value="threading">Pipe Threading</option>
                            <option value="fabrication">Custom Fabrication</option>
                            <option value="emergency">Emergency Repair</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Pipe Material</label>
                        <select id="pipeMaterial" class="form-control" required>
                            <option value="">Select Material</option>
                            <option value="stainless-steel">Stainless Steel</option>
                            <option value="carbon-steel">Carbon Steel</option>
                            <option value="aluminum">Aluminum</option>
                            <option value="copper">Copper</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Pipe Diameter (inches)</label>
                        <input type="number" id="pipeDiameter" class="form-control" step="0.1" required>
                    </div>
                    <div class="form-group">
                        <label>Estimated Hours</label>
                        <input type="number" id="estimatedHours" class="form-control" min="1" required>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Project Description</label>
                        <textarea id="projectDescription" class="form-control" rows="4" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Contact Name</label>
                        <input type="text" id="contactName" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="contactEmail" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" id="contactPhone" class="form-control" required>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <button type="submit" class="btn btn-success">Submit Service Request</button>
                    </div>
                </form>
            </div>
            
            <h3>Available Services</h3>
            <div id="servicesContainer" class="grid"></div>
        </div>
        
        <!-- Products Tab -->
        <div id="products" class="tab-content">
            <h2>Pipe Supplies & Equipment</h2>
            <div class="card">
                <div class="search-container">
                    <input type="text" id="productSearch" placeholder="Search pipes, tools, equipment..." class="form-control">
                    <i class="fas fa-search search-icon"></i>
                </div>
            </div>
            <div id="productsContainer" class="grid"></div>
        </div>
        
        <!-- Cart Tab -->
        <div id="cart" class="tab-content">
            <h2>Shopping Cart</h2>
            <div id="cartContainer"></div>
            <div class="card">
                <h3>Order Summary</h3>
                <div id="cartSummary"></div>
                <button class="btn btn-success" onclick="checkout()">Proceed to Checkout</button>
            </div>
        </div>
        
        <!-- Orders Tab -->
        <div id="orders" class="tab-content">
            <h2>My Orders & Service Requests</h2>
            <div class="card">
                <h3>Service Requests</h3>
                <div id="serviceRequests"></div>
            </div>
            <div class="card">
                <h3>Product Orders</h3>
                <div id="productOrders"></div>
            </div>
        </div>
        
        <!-- Admin Tab -->
        <div id="admin" class="tab-content">
            <h2>Admin Panel - Manage Products</h2>
            <div class="card">
                <h3>Add New Product</h3>
                <form id="productForm" class="grid-2">
                    <div class="form-group">
                        <label>Product Name</label>
                        <input type="text" id="productName" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select id="productCategory" class="form-control" required>
                            <option value="">Select Category</option>
                            <option value="pipes">Pipes</option>
                            <option value="tools">Tools</option>
                            <option value="machines">Machines</option>
                            <option value="accessories">Accessories</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Price</label>
                        <input type="number" id="productPrice" class="form-control" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label>Unit</label>
                        <input type="text" id="productUnit" class="form-control" value="foot" required>
                    </div>
                    <div class="form-group">
                        <label>Stock Quantity</label>
                        <input type="number" id="productStock" class="form-control" required>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Description</label>
                        <textarea id="productDescription" class="form-control" rows="3" required></textarea>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Features (comma separated)</label>
                        <input type="text" id="productFeatures" class="form-control" placeholder="Feature 1, Feature 2, Feature 3">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Product Image URL</label>
                        <input type="url" id="productImage" class="form-control" placeholder="https://example.com/image.jpg">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <button type="submit" class="btn btn-success">Add Product</button>
                    </div>
                </form>
            </div>
            
            <h3>Existing Products</h3>
            <div id="adminProducts" class="grid"></div>
        </div>
    </div>

    <script>
        // Global variables
        let shoppingCart = JSON.parse(localStorage.getItem('pipeDrillCart')) || [];
        let serviceRequests = JSON.parse(localStorage.getItem('pipeDrillServiceRequests')) || [];
        let productOrders = JSON.parse(localStorage.getItem('pipeDrillProductOrders')) || [];
        
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Find and activate the clicked tab button
            const tabButtons = document.querySelectorAll('.nav-tab');
            for (let tab of tabButtons) {
                if (tab.textContent.includes(tabName.charAt(0).toUpperCase() + tabName.slice(1)) || 
                    (tabName === 'home' && tab.textContent.includes('Home'))) {
                    tab.classList.add('active');
                    break;
                }
            }
            
            // Update cart count
            updateCartCount();
            
            // Load content based on tab
            if (tabName === 'cart') updateCartDisplay();
            if (tabName === 'orders') loadOrders();
            if (tabName === 'products') loadProducts();
            if (tabName === 'services') loadServices();
            if (tabName === 'admin') loadAdminProducts();
        }
        
        function updateCartCount() {
            const count = shoppingCart.reduce((total, item) => total + item.quantity, 0);
            document.getElementById('cartCount').textContent = count;
        }
        
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Service request form handler
        document.getElementById('serviceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                service_type: document.getElementById('serviceType').value,
                pipe_material: document.getElementById('pipeMaterial').value,
                pipe_diameter: document.getElementById('pipeDiameter').value,
                estimated_hours: document.getElementById('estimatedHours').value,
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
                    // Also save to localStorage for demo
                    const serviceRequest = {
                        id: Date.now(),
                        ...formData,
                        status: 'pending',
                        date: new Date().toLocaleDateString()
                    };
                    serviceRequests.push(serviceRequest);
                    localStorage.setItem('pipeDrillServiceRequests', JSON.stringify(serviceRequests));
                    
                    showNotification('Service request submitted successfully!');
                    e.target.reset();
                } else {
                    showNotification('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Network error. Please try again.', 'error');
            }
        });
        
        // Product form handler for admin
        document.getElementById('productForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('productName').value,
                category: document.getElementById('productCategory').value,
                price: parseFloat(document.getElementById('productPrice').value),
                unit: document.getElementById('productUnit').value,
                stock: parseInt(document.getElementById('productStock').value),
                description: document.getElementById('productDescription').value,
                features: document.getElementById('productFeatures').value.split(',').map(f => f.trim()).filter(f => f),
                image: document.getElementById('productImage').value || 'https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400'
            };
            
            try {
                const response = await fetch('/api/add-product', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification('Product added successfully!');
                    e.target.reset();
                    loadAdminProducts();
                    loadProducts(); // Refresh products tab
                } else {
                    showNotification('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Network error. Please try again.', 'error');
            }
        });
        
        // Load products from API with image support
        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('productsContainer');
                    container.innerHTML = data.products.map(product => `
                        <div class="product-card">
                            <div class="product-image">
                                ${product.image ? 
                                    `<img src="${product.image}" alt="${product.name}" onerror="this.src='https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400'">` :
                                    `<div class="image-placeholder">
                                        <i class="fas fa-box"></i>
                                    </div>`
                                }
                            </div>
                            <h3>${product.name}</h3>
                            <p>${product.description}</p>
                            <p class="price">$${product.price.toFixed(2)}/${product.unit}</p>
                            <p>Stock: ${product.stock}</p>
                            <div style="margin: 10px 0;">
                                ${product.features.map(feature => 
                                    `<span class="feature-tag">${feature}</span>`
                                ).join('')}
                            </div>
                            <button class="btn btn-primary" onclick="addToCart(${product.id})">
                                Add to Cart
                            </button>
                        </div>
                    `).join('');
                    
                    // Add search functionality
                    document.getElementById('productSearch').addEventListener('input', function(e) {
                        const searchTerm = e.target.value.toLowerCase();
                        const filteredProducts = data.products.filter(product => 
                            product.name.toLowerCase().includes(searchTerm) || 
                            product.description.toLowerCase().includes(searchTerm) ||
                            product.category.toLowerCase().includes(searchTerm)
                        );
                        
                        container.innerHTML = filteredProducts.map(product => `
                            <div class="product-card">
                                <div class="product-image">
                                    ${product.image ? 
                                        `<img src="${product.image}" alt="${product.name}" onerror="this.src='https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400'">` :
                                        `<div class="image-placeholder">
                                            <i class="fas fa-box"></i>
                                        </div>`
                                    }
                                </div>
                                <h3>${product.name}</h3>
                                <p>${product.description}</p>
                                <p class="price">$${product.price.toFixed(2)}/${product.unit}</p>
                                <p>Stock: ${product.stock}</p>
                                <div style="margin: 10px 0;">
                                    ${product.features.map(feature => 
                                        `<span class="feature-tag">${feature}</span>`
                                    ).join('')}
                                </div>
                                <button class="btn btn-primary" onclick="addToCart(${product.id})">
                                    Add to Cart
                                </button>
                            </div>
                        `).join('');
                    });
                }
            } catch (error) {
                console.error('Error loading products:', error);
                // Fallback to demo data
                loadDemoProducts();
            }
        }
        
        // Load admin products
        async function loadAdminProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('adminProducts');
                    container.innerHTML = data.products.map(product => `
                        <div class="product-card">
                            <div class="product-image">
                                ${product.image ? 
                                    `<img src="${product.image}" alt="${product.name}" onerror="this.src='https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400'">` :
                                    `<div class="image-placeholder">
                                        <i class="fas fa-box"></i>
                                    </div>`
                                }
                            </div>
                            <h3>${product.name}</h3>
                            <p>${product.description}</p>
                            <p class="price">$${product.price.toFixed(2)}/${product.unit}</p>
                            <p>Stock: ${product.stock}</p>
                            <div style="margin: 10px 0;">
                                ${product.features.map(feature => 
                                    `<span class="feature-tag">${feature}</span>`
                                ).join('')}
                            </div>
                            <button class="btn btn-danger" onclick="deleteProduct(${product.id})">
                                Delete Product
                            </button>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading admin products:', error);
            }
        }
        
        // Delete product function
        async function deleteProduct(productId) {
            if (!confirm('Are you sure you want to delete this product?')) return;
            
            try {
                const response = await fetch('/api/delete-product/' + productId, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                if (result.success) {
                    showNotification('Product deleted successfully!');
                    loadAdminProducts();
                    loadProducts();
                } else {
                    showNotification('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Network error. Please try again.', 'error');
            }
        }
        
        // Demo products fallback
        function loadDemoProducts() {
            const demoProducts = [
                {
                    id: 1, name: "Stainless Steel Pipe 2-inch", 
                    description: "304 Stainless steel pipe, 2-inch diameter, schedule 40",
                    price: 12.50, unit: "foot", stock: 150,
                    features: ["Corrosion resistant", "Food grade", "Weldable"],
                    image: "https://images.unsplash.com/photo-1581093458799-108dc8c4511a?w=400"
                }
            ];
            
            const container = document.getElementById('productsContainer');
            container.innerHTML = demoProducts.map(product => `
                <div class="product-card">
                    <div class="product-image">
                        <img src="${product.image}" alt="${product.name}">
                    </div>
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <p class="price">$${product.price.toFixed(2)}/${product.unit}</p>
                    <p>Stock: ${product.stock}</p>
                    <div style="margin: 10px 0;">
                        ${product.features.map(feature => 
                            `<span class="feature-tag">${feature}</span>`
                        ).join('')}
                    </div>
                    <button class="btn btn-primary" onclick="addToCart(${product.id})">
                        Add to Cart
                    </button>
                </div>
            `).join('');
        }
        
        // Load services from API with image support
        async function loadServices() {
            try {
                const response = await fetch('/api/services');
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('servicesContainer');
                    container.innerHTML = data.services.map(service => `
                        <div class="service-card">
                            <div class="product-image">
                                ${service.image ? 
                                    `<img src="${service.image}" alt="${service.name}" onerror="this.src='https://images.unsplash.com/photo-1581094794322-3a6e3c8aa330?w=400'">` :
                                    `<div class="image-placeholder">
                                        <i class="fas fa-cogs"></i>
                                    </div>`
                                }
                            </div>
                            <h3>${service.name}</h3>
                            <p>${service.description}</p>
                            <p class="price">$${service.hourly_rate}/hour</p>
                            <div style="margin: 10px 0;">
                                ${service.features.map(feature => 
                                    `<span class="feature-tag">${feature}</span>`
                                ).join('')}
                            </div>
                            <button class="btn btn-outline" onclick="bookService(${service.id})">
                                Book This Service
                            </button>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading services:', error);
                // Fallback to demo services
                loadDemoServices();
            }
        }
        
        // Demo services fallback
        function loadDemoServices() {
            const demoServices = [
                {
                    id: 1, name: "Precision Pipe Drilling",
                    description: "Professional pipe drilling service with precision accuracy",
                    hourly_rate: 85.00,
                    features: ["Laser guided", "CAD/CAM support", "Quality certification"],
                    image: "https://images.unsplash.com/photo-1581094794322-3a6e3c8aa330?w=400"
                }
            ];
            
            const container = document.getElementById('servicesContainer');
            container.innerHTML = demoServices.map(service => `
                <div class="service-card">
                    <div class="product-image">
                        <img src="${service.image}" alt="${service.name}">
                    </div>
                    <h3>${service.name}</h3>
                    <p>${service.description}</p>
                    <p class="price">$${service.hourly_rate}/hour</p>
                    <div style="margin: 10px 0;">
                        ${service.features.map(feature => 
                            `<span class="feature-tag">${feature}</span>`
                        ).join('')}
                    </div>
                    <button class="btn btn-outline" onclick="bookService(${service.id})">
                        Book This Service
                    </button>
                </div>
            `).join('');
        }
        
        // Shopping cart functions
        async function addToCart(productId) {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();
                const product = data.products.find(p => p.id === productId);
                
                if (!product) {
                    showNotification('Product not found', 'error');
                    return;
                }
                
                const existingItem = shoppingCart.find(item => item.id === productId);
                if (existingItem) {
                    existingItem.quantity += 1;
                } else {
                    shoppingCart.push({
                        id: product.id,
                        name: product.name,
                        price: product.price,
                        quantity: 1,
                        unit: product.unit,
                        image: product.image
                    });
                }
                
                localStorage.setItem('pipeDrillCart', JSON.stringify(shoppingCart));
                updateCartCount();
                showNotification(`${product.name} added to cart!`);
            } catch (error) {
                showNotification('Error adding product to cart', 'error');
            }
        }
        
        function updateCartDisplay() {
            const container = document.getElementById('cartContainer');
            const summary = document.getElementById('cartSummary');
            
            if (shoppingCart.length === 0) {
                container.innerHTML = '<div class="card"><p>Your cart is empty</p></div>';
                summary.innerHTML = '<p>Total: $0.00</p>';
                return;
            }
            
            container.innerHTML = shoppingCart.map(item => `
                <div class="cart-item card">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        ${item.image ? 
                            `<img src="${item.image}" alt="${item.name}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">` :
                            `<div style="width: 60px; height: 60px; background: #3498db; display: flex; align-items: center; justify-content: center; border-radius: 8px; color: white;">
                                <i class="fas fa-box"></i>
                            </div>`
                        }
                        <div>
                            <h4>${item.name}</h4>
                            <p>$${item.price.toFixed(2)}/${item.unit}</p>
                        </div>
                    </div>
                    <div class="quantity-controls">
                        <button class="btn btn-outline" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button class="btn btn-outline" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        <button class="btn btn-danger" onclick="removeFromCart(${item.id})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `).join('');
            
            const total = shoppingCart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            summary.innerHTML = `
                <p>Subtotal: $${total.toFixed(2)}</p>
                <p>Tax (8%): $${(total * 0.08).toFixed(2)}</p>
                <p><strong>Total: $${(total * 1.08).toFixed(2)}</strong></p>
            `;
        }
        
        function updateQuantity(productId, newQuantity) {
            if (newQuantity < 1) {
                removeFromCart(productId);
                return;
            }
            
            const item = shoppingCart.find(item => item.id === productId);
            if (item) {
                item.quantity = newQuantity;
                localStorage.setItem('pipeDrillCart', JSON.stringify(shoppingCart));
                updateCartDisplay();
                updateCartCount();
            }
        }
        
        function removeFromCart(productId) {
            shoppingCart = shoppingCart.filter(item => item.id !== productId);
            localStorage.setItem('pipeDrillCart', JSON.stringify(shoppingCart));
            updateCartDisplay();
            updateCartCount();
            showNotification('Item removed from cart');
        }
        
        async function checkout() {
            if (shoppingCart.length === 0) {
                showNotification('Your cart is empty', 'error');
                return;
            }
            
            try {
                const orderData = {
                    items: shoppingCart,
                    total: shoppingCart.reduce((sum, item) => sum + (item.price * item.quantity), 0) * 1.08
                };
                
                const response = await fetch('/api/place-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(orderData)
                });
                
                const result = await response.json();
                if (result.success) {
                    // Also save to localStorage for demo
                    const order = {
                        id: Date.now(),
                        items: [...shoppingCart],
                        date: new Date().toLocaleDateString(),
                        status: 'pending',
                        total: orderData.total
                    };
                    productOrders.push(order);
                    localStorage.setItem('pipeDrillProductOrders', JSON.stringify(productOrders));
                    
                    shoppingCart = [];
                    localStorage.setItem('pipeDrillCart', JSON.stringify(shoppingCart));
                    
                    updateCartDisplay();
                    updateCartCount();
                    
                    showNotification('Order placed successfully!');
                    switchTab('orders');
                } else {
                    showNotification('Error placing order: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Network error. Please try again.', 'error');
            }
        }
        
        async function loadOrders() {
            try {
                // Load service requests from API
                const serviceResponse = await fetch('/api/service-requests');
                const serviceData = await serviceResponse.json();
                
                const serviceRequestsContainer = document.getElementById('serviceRequests');
                if (serviceData.success && serviceData.requests.length > 0) {
                    serviceRequestsContainer.innerHTML = serviceData.requests.map(request => `
                        <div class="order-card">
                            <h4>${request.service_type.replace('-', ' ').toUpperCase()} - ${request.pipe_material}</h4>
                            <p>Diameter: ${request.pipe_diameter}" | Hours: ${request.estimated_hours}</p>
                            <p>Contact: ${request.contact_name} (${request.contact_phone})</p>
                            <p>Date: ${new Date(request.timestamp).toLocaleDateString()}</p>
                            <span class="order-status status-${request.status.toLowerCase()}">${request.status.toUpperCase()}</span>
                        </div>
                    `).join('');
                } else {
                    serviceRequestsContainer.innerHTML = '<p>No service requests found.</p>';
                }
                
                // Load product orders from API
                const orderResponse = await fetch('/api/product-orders');
                const orderData = await orderResponse.json();
                
                const productOrdersContainer = document.getElementById('productOrders');
                if (orderData.success && orderData.orders.length > 0) {
                    productOrdersContainer.innerHTML = orderData.orders.map(order => `
                        <div class="order-card">
                            <h4>Order #${order.id}</h4>
                            <p>Items: ${order.items.length} | Total: $${order.total.toFixed(2)}</p>
                            <p>Date: ${new Date(order.timestamp).toLocaleDateString()}</p>
                            <span class="order-status status-${order.status.toLowerCase()}">${order.status.toUpperCase()}</span>
                        </div>
                    `).join('');
                } else {
                    productOrdersContainer.innerHTML = '<p>No product orders found.</p>';
                }
            } catch (error) {
                console.error('Error loading orders:', error);
                // Fallback to localStorage data
                loadDemoOrders();
            }
        }
        
        function loadDemoOrders() {
            const serviceRequestsContainer = document.getElementById('serviceRequests');
            if (serviceRequests.length === 0) {
                serviceRequestsContainer.innerHTML = '<p>No service requests found.</p>';
            } else {
                serviceRequestsContainer.innerHTML = serviceRequests.map(request => `
                    <div class="order-card">
                        <h4>${request.service_type.replace('-', ' ').toUpperCase()} - ${request.pipe_material}</h4>
                        <p>Diameter: ${request.pipe_diameter}" | Hours: ${request.estimated_hours}</p>
                        <p>Contact: ${request.contact_name} (${request.contact_phone})</p>
                        <p>Date: ${request.date}</p>
                        <span class="order-status status-${request.status}">${request.status.toUpperCase()}</span>
                    </div>
                `).join('');
            }
            
            const productOrdersContainer = document.getElementById('productOrders');
            if (productOrders.length === 0) {
                productOrdersContainer.innerHTML = '<p>No product orders found.</p>';
            } else {
                productOrdersContainer.innerHTML = productOrders.map(order => `
                    <div class="order-card">
                        <h4>Order #${order.id}</h4>
                        <p>Items: ${order.items.length} | Total: $${order.total.toFixed(2)}</p>
                        <p>Date: ${order.date}</p>
                        <span class="order-status status-${order.status}">${order.status.toUpperCase()}</span>
                    </div>
                `).join('');
            }
        }
        
        function bookService(serviceId) {
            showNotification('Redirecting to service booking form...');
            // In a real app, this would pre-fill the service form
            switchTab('services');
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', () => {
            updateCartCount();
            loadProducts();
            loadServices();
        });
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def home():
    return HTML_PAGE

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/products')
def get_products():
    data = load_data(PRODUCTS_FILE)
    return jsonify({'success': True, 'products': data.get('products', [])})

@app.route('/api/services')
def get_services():
    data = load_data(PRODUCTS_FILE)
    return jsonify({'success': True, 'services': data.get('services', [])})

@app.route('/api/service-request', methods=['POST'])
def submit_service_request():
    try:
        data = request.get_json()
        requests = load_data(REQUESTS_FILE) or []
        
        new_request = {
            'id': len(requests) + 1,
            **data,
            'timestamp': datetime.now().isoformat(),
            'status': 'Pending',
            'type': 'service'
        }
        
        requests.append(new_request)
        save_data(REQUESTS_FILE, requests)
        
        return jsonify({'success': True, 'request_id': new_request['id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/place-order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        orders = load_data(ORDERS_FILE) or []
        
        new_order = {
            'id': len(orders) + 1,
            'items': data.get('items', []),
            'total': data.get('total', 0),
            'timestamp': datetime.now().isoformat(),
            'status': 'Processing',
            'type': 'product'
        }
        
        orders.append(new_order)
        save_data(ORDERS_FILE, orders)
        
        return jsonify({'success': True, 'order_id': new_order['id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/service-requests')
def get_service_requests():
    requests = load_data(REQUESTS_FILE) or []
    service_requests = [r for r in requests if r.get('type') == 'service']
    return jsonify({'success': True, 'requests': service_requests})

@app.route('/api/product-orders')
def get_product_orders():
    orders = load_data(ORDERS_FILE) or []
    product_orders = [o for o in orders if o.get('type') == 'product']
    return jsonify({'success': True, 'orders': product_orders})

@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        products_data = load_data(PRODUCTS_FILE)
        products = products_data.get('products', [])
        
        new_product = {
            'id': max([p['id'] for p in products], default=0) + 1,
            **data
        }
        
        products.append(new_product)
        products_data['products'] = products
        save_data(PRODUCTS_FILE, products_data)
        
        return jsonify({'success': True, 'product_id': new_product['id']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        products_data = load_data(PRODUCTS_FILE)
        products = products_data.get('products', [])
        
        products = [p for p in products if p['id'] != product_id]
        products_data['products'] = products
        save_data(PRODUCTS_FILE, products_data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_data()
    app.run(debug=True, port=5000)