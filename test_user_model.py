"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from app import app
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///warbler_test'


# Now we can import app



# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

def user(n):
    return  User(
            email=f"test@test.com{n}",
            username=f"testuser{n}",
            password=f"HASHED_PASSWORD{n}"
        )

def sign():
    return User.signup(
        username='testuser',
        password='hashed_pass', 
        email='test@test.com', 
        image_url='Google.com'
    )

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

      

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = user(1)

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        u = user(1)

        db.session.add(u)
        db.session.commit()
       
        self.assertIn('testuser1, test@test.com1', repr(u))
    
    def test_when_following(self):
        u1 = user(1)
        u2 = user(2)
        db.session.add_all([u1,u2])
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()

        self.assertIsInstance(u1.following, list)
        self.assertEqual(len(u1.following), 1)
        self.assertEqual(u1.following[0].id, u2.id)
        self.assertEqual(u1.following[0].username, "testuser2")
        self.assertTrue(u1.is_following(u2))
    
    def test_when_not_following(self):
        u1 = user(1)
        u2 = user(2)
        db.session.add_all([u1,u2])
        db.session.commit()

        self.assertEqual(len(u1.following), 0)
        self.assertIsInstance(u1.following, list)
        self.assertFalse(u1.is_following(u2))

    def test_when_is_followed(self):
        u1 = user(1)
        u2 = user(2)
        db.session.add_all([u1,u2])
        db.session.commit()

        u2.following.append(u1)
        db.session.commit()
        
        
        self.assertIsInstance(u1.followers, list)
        self.assertEqual(len(u1.followers), 1)
        self.assertEqual(u1.followers[0].id, u2.id)
        self.assertEqual(u1.followers[0].username, "testuser2")
        self.assertTrue(u1.is_followed_by(u2))

    def test_when_is_not_followed(self):
        u1 = user(1)
        u2 = user(2)
        db.session.add_all([u1,u2])
        db.session.commit()
        
        self.assertEqual(len(u1.followers), 0)
        self.assertIsInstance(u1.followers, list)
        self.assertFalse(u1.is_followed_by(u2))

    def test_create_user(self):
        user1 = sign()
        db.session.add(user1)
        db.session.commit()
        

        self.assertEqual(user1.id, User.query.first().id)
        self.assertEqual(user1.image_url, User.query.first().image_url)

    def test_password_hashed(self):
        pass_word = 'hashed_pass'
        user1 = sign()
        db.session.add(user1)
        db.session.commit()

        self.assertNotEqual(user1.password, pass_word)
        self.assertIn('$2b$12', user1.password)

    def test_authentication(self):
        user1 = sign()
        db.session.add(user1)
        db.session.commit()
        u = User.authenticate(username=user1.username, password='hashed_pass')
        
        self.assertEqual(user1.id, u.id)
        self.assertEqual(user1.password, u.password)

    def test_wrong_username(self):
        user1 = sign()
        db.session.add(user1)
        db.session.commit()
        u = User.authenticate(username='bob', password='hashed_pass')

        self.assertFalse(u)
    
    def test_wrong_password(self):
        user1 = sign()
        db.session.add(user1)
        db.session.commit()
        u = User.authenticate(username=user1.username, password='pass')

        self.assertFalse(u)