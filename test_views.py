import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models

class TestViews(unittest.TestCase):

    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #the basedir lines could be added like the original db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_homeroute(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_marketroute(self):
        response = self.app.get('/market', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_signuproute(self):
        response = self.app.get('/signUp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_loginroute(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Ensure that home page loads as required
    def test_home(self):
        response = self.app.get('/home', follow_redirects=True)
        self.assertIn(b'Welcome to The Pokemon Market', response.data)

    # Ensure that market page requires user login
    def test_market_requires_login(self):
        response = self.app.get('/market', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)



if __name__ == '__main__':
    unittest.main()