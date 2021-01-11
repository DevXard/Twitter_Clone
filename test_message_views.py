"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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
db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_as_self(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            # test that message is added as youslef
            self.assertEqual(msg.user_id, self.testuser.id)

    def test_delete_message(self):
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        # create message to be deleated
        resp = c.post("/messages/new", data={"text": "Delete me"})

        # get msg ID
        msg_id = User.query.get(self.testuser.id).messages[0].id

        #Check msg exsists
        msg = Message.query.one()
        self.assertEqual(msg.text, "Delete me")

        # send request for deleting message
        resp = c.post(f"/messages/{msg_id}/delete")

        self.assertEqual(resp.status_code, 302)

        msg = Message.query.all()
        self.assertEqual(len(msg), 0)
        self.assertIsInstance(msg, list)

    def test_add_message_as_logedout(self):

        resp = self.client.post("/messages/new", data={"text": "Can you create?"})

        self.assertEqual(resp.status_code, 302)

        msg = Message.query.all()
        self.assertEqual(len(msg), 0)
        self.assertIsInstance(msg, list)
    
    def test_delete_message_when_logged(self):
        m = Message(text="Delete me", user_id=1)
        self.testuser.messages.append(m)
        db.session.commit()
        #Check msg exsists
        msg = Message.query.one()
        self.assertEqual(msg.text, "Delete me")


        # send request for deleting message
        resp = self.client.post(f"/messages/{msg.id}/delete")

        self.assertEqual(resp.status_code, 302)

        msg = Message.query.all()
        self.assertEqual(len(msg), 1)
        self.assertIsInstance(msg, list)
    
    