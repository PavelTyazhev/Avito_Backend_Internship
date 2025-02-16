from models import User, Transaction, Purchase
from app import db

def test_user_creation(app):
    with app.app_context():
        user = User(username='testuser')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.coins == 1000
        assert user.check_password('password')

def test_transaction(app):
    with app.app_context():
        sender = User(username='sender')
        receiver = User(username='receiver')
        db.session.add_all([sender, receiver])
        db.session.commit()
        
        transaction = Transaction(
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=100
        )
        db.session.add(transaction)
        db.session.commit()
        
        assert transaction.id is not None
        assert transaction.sender == sender
        assert transaction.receiver == receiver

def test_purchase(app):
    with app.app_context():
        user = User(username='buyer')
        db.session.add(user)
        db.session.commit()
        
        purchase = Purchase(
            user_id=user.id,
            item='t-shirt',
            price=80
        )
        db.session.add(purchase)
        db.session.commit()
        
        assert purchase.id is not None
        assert purchase.user == user