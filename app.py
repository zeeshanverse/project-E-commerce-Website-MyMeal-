from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.secret_key = 'my_secret_key'  # Secret key for session

# Sample menu items with 6 options
menu_items = [
    {'item': 'Masala Dosa', 'price': 30},
    {'item': 'Paneer Dosa', 'price': 50},
    {'item': 'Aloo Pratha', 'price': 40},
    {'item': 'Paneer Pratha', 'price': 60},
    {'item': 'Pizza', 'price': 250},
    {'item': 'Burger', 'price': 150}
]

@app.route('/')
def index():
    session['cart'] = []  # Initialize or reset the cart
    return render_template('index.html')

@app.route('/home')
def home():
    return redirect(url_for('order'))  # Redirect to order page

@app.route('/order')
def order():
    return render_template('order.html', menu_items=menu_items)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    service_type = request.form.get('service-type')
    home_address = None
    venue_address = None
    
    if service_type == 'bulk-delivery':
        home_address = request.form.get('home-address')
        flash(f'Bulk delivery request submitted! Home address: {home_address}', 'success')
    elif service_type == 'food-catering':
        venue_address = request.form.get('venue-address')
        flash(f'Food catering request submitted! Venue address: {venue_address}', 'success')
    else:
        flash('Please select a valid service type.', 'error')
        return redirect(url_for('home'))
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')  # Create this template for the thank you message

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        service_type = request.form['serviceType']
        address = request.form.get('homeAddress', request.form.get('venueAddress'))
        message = request.form['message']

        print(f"Name: {name}, Email: {email}, Phone: {phone}, Service: {service_type}, Address: {address}, Message: {message}")
        
        return redirect(url_for('thank_you'))
    
    return render_template('contact.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item')
    item_price = int(request.form.get('price'))

    if 'cart' not in session:
        session['cart'] = []  # Initialize an empty cart if it doesn't exist

    # Check if item already exists in cart
    for item in session['cart']:
        if item['item'] == item_name:
            item['quantity'] += 1  # Increase quantity by 1
            break
    else:
        # If item is not in the cart, add it
        session['cart'].append({'item': item_name, 'price': item_price, 'quantity': 1})

    session.modified = True  # Mark session as modified to ensure changes are saved
    return redirect(url_for('order'))  # Redirect to the order page 

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_name = request.form.get('item')
    cart = session.get('cart', [])

    for item in cart:
        if item['item'] == item_name:
            if item['quantity'] > 1:
                item['quantity'] -= 1  # Decrease quantity by 1
            else:
                cart.remove(item)  # Remove item if quantity is 1
            break  # Exit after updating the item quantity

    session['cart'] = cart
    session.modified = True

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total_amount=total_amount)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    if request.method == 'POST':
        # Capture common checkout details
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        payment_method = request.form.get('payment_method')
        
        # Ensure basic details are filled in
        if not name or not address or not phone or not payment_method:
            flash('All fields are required for checkout', 'error')
            return redirect(url_for('checkout'))
        
        # Handle payment-specific details
        if payment_method == 'card':
            card_number = request.form.get('card_number')
            expiry_date = request.form.get('expiry_date')
            cvv = request.form.get('cvv')
            
            if not card_number or not expiry_date or not cvv:
                flash('Please enter all card details.', 'error')
                return redirect(url_for('checkout'))
            # Process card payment logic here (e.g., integrate with payment gateway)

        elif payment_method == 'wallet':
            wallet_number = request.form.get('wallet_number')
            
            if not wallet_number:
                flash('Please enter your digital wallet number.', 'error')
                return redirect(url_for('checkout'))
            # Process wallet payment logic here

        # Process the order (store order in database, etc.)
        session.pop('cart', None)  # Clear cart after placing the order
        flash(f'Thank you, {name}! Your order has been placed.', 'success')
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', cart=cart_items, total_amount=total_amount)

@app.route('/place-order', methods=['POST'])
def place_order():
    data = request.get_json()
    print(data)
    return jsonify({"message": "Order successfully placed!"})
    return redirect(url_for('thank_you'))  # Ensure 'thank_you' matches the route name for thankyou.html

if __name__ == '__main__':
    app.run(debug=True)
