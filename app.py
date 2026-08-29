from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "my_secret_key"

menu_items = [
    {
        "item": "Masala Dosa",
        "price": 30,
        "image": "masaladosa.jpg",
        "category": "South Indian",
        "description": "Crispy dosa filled with a flavorful spiced potato masala."
    },
    {
        "item": "Paneer Dosa",
        "price": 50,
        "image": "paneerdosa.jpg",
        "category": "South Indian",
        "description": "Crispy dosa with a spicy paneer filling and Indian spices."
    },
    {
        "item": "Aloo Pratha",
        "price": 40,
        "image": "aloopratha.jpg",
        "category": "North Indian",
        "description": "Golden stuffed paratha filled with seasoned potato and herbs."
    },
    {
        "item": "Paneer Pratha",
        "price": 60,
        "image": "paneerpratha.jpg",
        "category": "North Indian",
        "description": "Soft paratha stuffed with spiced paneer, herbs and onions."
    },
    {
        "item": "Pizza",
        "price": 250,
        "image": "pizza.jpeg",
        "category": "Fast Food",
        "description": "Cheesy pizza with a crisp base and classic savory toppings."
    },
    {
        "item": "Burger",
        "price": 150,
        "image": "burger.jpeg",
        "category": "Fast Food",
        "description": "Juicy burger served in a soft bun with fresh toppings."
    },
    {
        "item": "Chilli Potatoes",
        "price": 80,
        "image": "chilli.jpeg",
        "category": "Starters",
        "description": "Crispy potato fingers tossed in a bold Indo-Chinese sauce."
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return redirect(url_for("order"))


@app.route("/order")
def order():
    cart = session.get("cart", [])
    cart_count = sum(item["quantity"] for item in cart)
    return render_template(
        "order.html",
        menu_items=menu_items,
        cart_count=cart_count
    )


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item_name = request.form.get("item")
    item_price = request.form.get("price")

    if not item_name or not item_price:
        flash("Invalid item.", "error")
        return redirect(url_for("order"))

    try:
        item_price = int(item_price)
    except ValueError:
        flash("Invalid item price.", "error")
        return redirect(url_for("order"))

    if "cart" not in session:
        session["cart"] = []

    for item in session["cart"]:
        if item["item"] == item_name:
            item["quantity"] += 1
            break
    else:
        session["cart"].append({
            "item": item_name,
            "price": item_price,
            "quantity": 1
        })

    session.modified = True
    flash(f"{item_name} added to your cart.", "success")
    return redirect(url_for("order"))


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    item_name = request.form.get("item")
    cart = session.get("cart", [])

    for item in cart:
        if item["item"] == item_name:
            if item["quantity"] > 1:
                item["quantity"] -= 1
            else:
                cart.remove(item)
            break

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total_amount = sum(
        item["price"] * item["quantity"] for item in cart_items
    )
    cart_count = sum(item["quantity"] for item in cart_items)

    return render_template(
        "cart.html",
        cart=cart_items,
        total_amount=total_amount,
        cart_count=cart_count
    )


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items = session.get("cart", [])
    total_amount = sum(
        item["price"] * item["quantity"] for item in cart_items
    )

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        payment_method = request.form.get("payment_method", "").strip()

        if not name or not address or not phone or not payment_method:
            flash("Please complete all required checkout fields.", "error")
            return redirect(url_for("checkout"))

        if payment_method == "card":
            card_number = request.form.get("card_number", "").strip()
            expiry_date = request.form.get("expiry_date", "").strip()
            cvv = request.form.get("cvv", "").strip()

            if not card_number or not expiry_date or not cvv:
                flash("Please enter all card details.", "error")
                return redirect(url_for("checkout"))

        elif payment_method == "wallet":
            wallet_number = request.form.get("wallet_number", "").strip()

            if not wallet_number:
                flash("Please enter your wallet number.", "error")
                return redirect(url_for("checkout"))

        elif payment_method != "cod":
            flash("Please select a valid payment method.", "error")
            return redirect(url_for("checkout"))

        session.pop("cart", None)
        flash(f"Thank you, {name}! Your order has been placed.", "success")
        return redirect(url_for("thank_you"))

    return render_template(
        "checkout.html",
        cart=cart_items,
        total_amount=total_amount
    )


@app.route("/place-order", methods=["POST"])
def place_order():
    # Supports the checkout form and keeps the route compatible
    # with JSON clients such as Postman.
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    if not data:
        return jsonify({"message": "No order details received."}), 400

    if not session.get("cart"):
        return jsonify({"message": "Your cart is empty."}), 400

    session.pop("cart", None)

    if request.is_json:
        return jsonify({"message": "Order successfully placed!"}), 200

    flash("Your order has been placed successfully.", "success")
    return redirect(url_for("thank_you"))


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    service_type = request.form.get("service-type")
    home_address = request.form.get("home-address")
    venue_address = request.form.get("venue-address")

    if not name or not email or not phone or not service_type:
        flash("Please complete all required fields.", "error")
        return redirect(url_for("contact"))

    if service_type == "bulk-delivery" and not home_address:
        flash("Please provide the delivery address.", "error")
        return redirect(url_for("contact"))

    if service_type == "food-catering" and not venue_address:
        flash("Please provide the venue address.", "error")
        return redirect(url_for("contact"))

    flash("Your request has been submitted successfully.", "success")
    return redirect(url_for("thank_you"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return submit()
    return render_template("contact.html")


@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
