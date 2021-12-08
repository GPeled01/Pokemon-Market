import os
import unittest
from flask import Flask
from flask import request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app import app, db, bcrypt, login_manager
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from app.models import Trainer, Pokemon

class TestTrainer(unittest.TestCase):

    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        admin = Trainer(trainername="Admin", email="admin@gmail.com", password="adminadmin")
        db.session.add(admin)
        db.session.commit()
        pass

    def tearDown(self):
        if current_user and current_user.is_authenticated:
            logout_user()
        db.session.remove()
        db.drop_all()

    # Ensure trainer can sign up
    def test_trainer_sign_up(self):
        with self.app:
            response = self.app.post('/signUp', data=dict(
                trainername='Test', email='test@gmail.com',
                password='testtest', password_confirmation='testtest'
            ), follow_redirects=True)
            self.assertIn(b'Trainer account created! You are now logged in as: Test', response.data)
            self.assertEqual(current_user.trainername, "Test")
            self.assertTrue(current_user.is_active)
            trainer = Trainer.query.filter_by(email='test@gmail.com').first()
            self.assertEqual(str(trainer), 'Trainer Test')

    # Ensure errors are thrown when sign up with incorrect email
    def test_incorrect_email_sign_up(self):
        with self.app:
            response = self.app.post('/signUp', data=dict(
                trainername='Test', email='test',
                password='testtest', password_confirmation='testtest'
            ), follow_redirects=True)
            self.assertIn(b'Invalid email address.', response.data)
            self.assertIn('/signUp', request.url)

    # Ensure errors are thrown when sign up with unmatched password and password confirmation
    def test_incorrect_password_confirmation_sign_up(self):
        with self.app:
            response = self.app.post('/signUp', data=dict(
                trainername='Test', email='test@gmail.com',
                password='testtest', password_confirmation='wrongwrong'
            ), follow_redirects=True)
            self.assertIn(b'Field must be equal to password.', response.data)
            self.assertIn('/signUp', request.url)

    # Ensure id is correct for the current logged in trainer
    def test_get_by_id(self):
        with self.app:
            self.app.post('/login', data=dict(
                trainername="Admin", password='adminadmin'
            ), follow_redirects=True)
            self.assertEqual(current_user.id, 1)
            self.assertNotEqual(current_user.id, 20)

    # Ensure given password is correct after unhashing
    def test_check_password(self):
        trainer = Trainer.query.filter_by(email='admin@gmail.com').first()
        self.assertTrue(trainer.checkPassword('adminadmin'))
        self.assertFalse(trainer.checkPassword('blabla'))

    # Ensure login behaves correctly with correct credentials
    def test_correct_login(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=dict(trainername="Admin", password="adminadmin"),
                follow_redirects=True
            )
            self.assertIn(b'Successfully logged in as: Admin', response.data)
            self.assertEqual(current_user.trainername, "Admin")
            self.assertTrue(current_user.is_active)

    # Ensure login behaves correctly with incorrect credentials
    def test_incorrect_login(self):
        response = self.app.post(
            '/login',
            data=dict(trainername="wrong", password="wrongwrong"),
            follow_redirects=True
        )
        self.assertIn(b'Trainer name and password do not match! Please try again', response.data)

    # Ensure logout behaves correctly
    def test_logout(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(trainername="Admin", password="adminadmin"),
                follow_redirects=True
            )
            response = self.app.get('/logout', follow_redirects=True)
            self.assertIn(b'Successfully logged out!', response.data)
            self.assertFalse(current_user.is_active)

    # Ensure that logout page requires user login
    def test_logout_route_requires_login(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    # Ensure change password behaves correctly with correct credentials
    def test_correct_change_password(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=dict(trainername="Admin", password="adminadmin"),
                follow_redirects=True
            )
            response = self.app.post('/changePassword', data=dict(old_password="adminadmin", new_password="newnewnew", password_confirmation="newnewnew"), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your password have been changed successfully.', response.data)
            self.assertFalse(current_user.is_active)
            trainer = Trainer.query.filter_by(trainername='Admin').first()
            self.assertFalse(trainer.checkPassword('adminadmin'))
            self.assertTrue(trainer.checkPassword('newnewnew'))
            self.assertIn('/login', request.url)

    # Ensure change password behaves correctly with correct credentials
    def test_incorrect_change_password(self):
        with self.app:
            response = self.app.post(
                    '/login',
                    data=dict(trainername="Admin", password="adminadmin"),
                    follow_redirects=True
            )
            response = self.app.post('/changePassword', data=dict(old_password="wrongwrong", new_password="newnewnew", password_confirmation="newnewnew"), follow_redirects=True)
            self.assertIn(b'Old password does not match! Please try again', response.data)
            self.assertIn('/changePassword', request.url)

if __name__ == '__main__':
    unittest.main()
