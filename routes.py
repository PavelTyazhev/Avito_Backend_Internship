from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Transaction, Purchase
from config import Config

api = Blueprint('api', __name__)
auth = Blueprint('auth', __name__)
shop = Blueprint('shop', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username=username)
            user.set_password(password)
            user.coins = Config.INITIAL_COINS
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
        elif not user.check_password(password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('shop.dashboard'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@shop.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('shop.dashboard'))
    return redirect(url_for('auth.login'))

@shop.route('/dashboard')
@login_required
def dashboard():
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    inventory = {}
    for purchase in purchases:
        inventory[purchase.item] = inventory.get(purchase.item, 0) + 1

    received = Transaction.query.filter_by(receiver_id=current_user.id).all()
    sent = Transaction.query.filter_by(sender_id=current_user.id).all()

    return render_template('dashboard.html', 
                         user=current_user,
                         inventory=inventory,
                         received=received,
                         sent=sent)

@shop.route('/shop')
@login_required
def shop_page():
    return render_template('shop.html', 
                         merchandise=Config.MERCHANDISE,
                         user=current_user)

@shop.route('/history')
@login_required
def history():
    received = Transaction.query.filter_by(receiver_id=current_user.id).all()
    sent = Transaction.query.filter_by(sender_id=current_user.id).all()
    return render_template('history.html',
                         received=received,
                         sent=sent)

@shop.route('/send-coins', methods=['POST'])
@login_required
def send_coins():
    receiver_username = request.form.get('receiver')
    amount = request.form.get('amount')

    if not receiver_username or not amount:
        flash('Please provide both recipient and amount', 'danger')
        return redirect(url_for('shop.dashboard'))

    try:
        amount = int(amount)
        if amount <= 0:
            flash('Amount must be positive', 'danger')
            return redirect(url_for('shop.dashboard'))
    except ValueError:
        flash('Invalid amount', 'danger')
        return redirect(url_for('shop.dashboard'))

    if amount > current_user.coins:
        flash('Insufficient coins', 'danger')
        return redirect(url_for('shop.dashboard'))

    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        flash('Recipient not found', 'danger')
        return redirect(url_for('shop.dashboard'))

    if receiver.id == current_user.id:
        flash('Cannot send coins to yourself', 'danger')
        return redirect(url_for('shop.dashboard'))

    current_user.coins -= amount
    receiver.coins += amount

    transaction = Transaction(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        amount=amount
    )

    db.session.add(transaction)
    db.session.commit()

    flash(f'Successfully sent {amount} coins to {receiver.username}', 'success')
    return redirect(url_for('shop.dashboard'))


@shop.route('/buy/<item>', methods=['POST'])
@login_required
def buy_item(item):
    if item not in Config.MERCHANDISE:
        flash('Item not found', 'danger')
        return redirect(url_for('shop.shop_page'))

    price = Config.MERCHANDISE[item]

    if current_user.coins < price:
        flash('Insufficient coins', 'danger')
        return redirect(url_for('shop.shop_page'))

    current_user.coins -= price
    purchase = Purchase(user_id=current_user.id, item=item, price=price)

    db.session.add(purchase)
    db.session.commit()

    flash(f'Successfully purchased {item}', 'success')
    return redirect(url_for('shop.shop_page'))

@api.route('/api/auth', methods=['POST'])
def auth_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'errors': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        user = User(username=username)
        user.set_password(password)
        user.coins = Config.INITIAL_COINS
        db.session.add(user)
        db.session.commit()
    elif not user.check_password(password):
        return jsonify({'errors': 'Invalid credentials'}), 401

    token = create_access_token(identity=username)
    return jsonify({'token': token}), 200

@api.route('/api/info', methods=['GET'])
@jwt_required()
def get_info():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'errors': 'User not found'}), 404

    purchases = Purchase.query.filter_by(user_id=user.id).all()
    inventory = {}
    for purchase in purchases:
        inventory[purchase.item] = inventory.get(purchase.item, 0) + 1

    inventory_list = [{"type": item, "quantity": qty} 
                     for item, qty in inventory.items()]

    received = Transaction.query.filter_by(receiver_id=user.id).all()
    sent = Transaction.query.filter_by(sender_id=user.id).all()

    received_list = [{"fromUser": t.sender.username, "amount": t.amount} 
                    for t in received]
    sent_list = [{"toUser": t.receiver.username, "amount": t.amount} 
                 for t in sent]

    return jsonify({
        "coins": user.coins,
        "inventory": inventory_list,
        "coinHistory": {
            "received": received_list,
            "sent": sent_list
        }
    })

@api.route('/api/sendCoin', methods=['POST'])
@jwt_required()
def send_coin():
    sender_username = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'toUser' not in data or 'amount' not in data:
        return jsonify({'errors': 'Missing required fields'}), 400

    amount = data['amount']
    receiver_username = data['toUser']

    if amount <= 0:
        return jsonify({'errors': 'Invalid amount'}), 400

    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not receiver:
        return jsonify({'errors': 'Recipient not found'}), 404

    if sender.coins < amount:
        return jsonify({'errors': 'Insufficient coins'}), 400

    sender.coins -= amount
    receiver.coins += amount

    transaction = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=amount
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': 'Transfer successful'}), 200

@api.route('/api/buy/<item>', methods=['GET'])
@jwt_required()
def buy_item_api(item):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if item not in Config.MERCHANDISE:
        return jsonify({'errors': 'Item not found'}), 404

    price = Config.MERCHANDISE[item]

    if user.coins < price:
        return jsonify({'errors': 'Insufficient coins'}), 400

    user.coins -= price
    purchase = Purchase(user_id=user.id, item=item, price=price)
    
    db.session.add(purchase)
    db.session.commit()

    return jsonify({'message': 'Purchase successful'}), 200