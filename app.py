from datetime import datetime

from flask import Flask, render_template, request, jsonify
import json
import requests
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'pavlywkwk@gmail.com'
app.config['MAIL_PASSWORD'] = 'qblb tcdx acxy ghto'
app.config['MAIL_DEFAULT_SENDER'] = 'pavlywkwk@gmail.com'


mail = Mail(app)

# Load products from JSON
with open('products.json', 'r') as f:
    products = json.load(f)

TELEGRAM_BOT_TOKEN = '7800979792:AAFbHUTQURsgyCAV_H5DDHq1A33rF-eVuo4'
TELEGRAM_CHAT_ID = '@ly168168168168168'

EMAIL_SENDER = 'your_email@example.com'
EMAIL_PASSWORD = 'your_password'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587


@app.route('/')
def catalog():
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('details.html', product=product)
    return 'Product not found', 404


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.form
        cart_items = json.loads(data.get('cart_items', '[]'))

        total = sum(item['price'] * item['quantity'] for item in cart_items)

        order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        context = {
            'order_id': order_id,
            'data': data,
            'cart_items': cart_items,
            'total': total,
            'business_name': "Boak Store"
        }

        html_content = render_template('invoice.html', **context)

        text_content = f"""
        Order Confirmation (Order #{order_id})
        --------------------------
        Customer: {data['name']}
        Email: {data['email']}
        Phone: {data['phone']}
        Address: {data['address']}
        --------------------------
        Order Items:
        """
        for item in cart_items:
            text_content += f"{item['name']} ({item['quantity']} × ${item['price']:.2f}) = ${item['price'] * item['quantity']:.2f}\n"
        text_content += f"\nTotal: ${total:.2f}\n\nThank you for your order!"

        # Prepare order details for Telegram (owner notification)
        order_details = (
            "\n"
            "🛒 NEW ORDER ALERT 🛒\n"
            "━━━━━━━━━━━━\n"
            f"👤 Customer: {data['name']}\n"
            f"📞 Contact: {data['phone']}\n"
            f"✉️ Email: {data['email']}\n"
            f"🏠 Address: {data['address']}\n"
            "━━━━━━━━━━━━\n"
            "🛍 ITEMS:\n"
        )

        for item in cart_items:
            order_details += f"   • {item['name']} — {item['quantity']} × ${item['price']} = ${item['price'] * item['quantity']:.2f}\n"

        order_details += (
            "━━━━━━━━━━━━\n"
            f"💰 TOTAL: ${total:.2f}\n"
            "━━━━━━━━━━━━"
        )

        # Send Telegram message to owner (optional)
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(telegram_url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': order_details})

        # Send email ONLY to customer
        try:
            msg = Message(
                f"Your Order Confirmation (#{order_id})",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[data['email']],
                body=text_content,
                html=html_content
            )
            mail.send(msg)
            app.logger.info(f"Order confirmation sent to customer: {data['email']}")
        except Exception as e:
            app.logger.error(f"Failed to send email to customer: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to send confirmation email'
            }), 500

        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order confirmation sent to your email',
        })

    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)