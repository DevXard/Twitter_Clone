from unittest import TestCase
from app import app
from datetime import datetime
from models import db, bcrypt, User, Message, Likes

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///warbler_test'

app.config['SQLALCHEMY_ECHO'] = False


#make Flask Errors be real Errors rather then HTML pages with errors
app.config['TESTING'] = True

#Dont use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserTestCase(TestCase):
    
    def setUp(self):
        """Clean up any existing pets."""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_messages(self):
        user = User(email='abc@123.com', username='M.jacson')
        message = Message(text= "Hi Yall", user_id=user.id)
        
        self.assertEqual(message.text, 'Hi Yall')
        self.assertEqual(message.user_id, user.id)
        self.assertIsInstance(user.messages, list)

    def test_user_messages(self):
        user = User(email='abc@123.com', username='M.jacson', password='123')
        db.session.add(user)
        db.session.commit()
        message = Message(text= "Hi Yall", user_id=user.id)
        db.session.add(message)
        db.session.commit()

        self.assertIsInstance(user.messages, list)
        self.assertEqual(len(user.messages), 1)

    def test_messages_like(self):
        user = User(email='abc@123.com', username='M.jacson', password='123')
        db.session.add(user)
        db.session.commit()
        message = Message(text= "Hi Yall", user_id=user.id)
        db.session.add(message)
        db.session.commit()
        like = Likes(user_id=user.id, message_id=message.id)
        db.session.add(like)
        db.session.commit()

        self.assertEqual(user.likes[0].id, message.id)
