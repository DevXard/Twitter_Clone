"""Users View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """ Test User View"""
    def setUp(self):
        """setUp users"""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user = User.signup("testuser", "test@test.com", "testuser", None)
        self.id = 2131
        self.user.id = self.id
        self.user1 = User.signup("testuser1", "test1@test.com", "testuser", None)
        self.user2 = User.signup("testuser2", "test2@test.com", "testuser", None)
        self.user3 = User.signup("testuser3", "test3@test.com", "testuser", None)
        self.user4 = User.signup("Shadow", "test4@test.com", "testuser", None)

        db.session.commit()
        

    def test_users_page(self):
        with self.client as c:
            res = c.get('users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('testuser', html)
            self.assertIn('testuser1', html)
            self.assertIn('testuser2', html)
            self.assertIn('testuser3', html)

    def test_show_user(self):
        with self.client as c:
            res = c.get(f'/users/{self.id}')
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('testuser', html)
            self.assertNotIn('testuser1', html)

    def test_search(self):
        with self.client as c:
            res = c.get('/users?q=Shadow')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Shadow', html)
            self.assertNotIn('testuser', html)
            self.assertNotIn('testuser1', html)
            self.assertNotIn('testuser2', html)
            self.assertNotIn('testuser3', html)