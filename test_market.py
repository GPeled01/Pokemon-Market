import os
import unittest
from flask import Flask
from flask import request, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app import app, db, bcrypt, login_manager
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from app.models import Trainer, Pokemon
from flask_wtf import FlaskForm
from app.forms import CatchPokemonForm, SellPokemonForm

class TestMarket(unittest.TestCase):

    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        admin = Trainer(trainername="Admin", email="admin@gmail.com", password="adminadmin")
        ratata = Pokemon(name="Ratata", price=100, type="Normal", description="Its fangs are long and very sharp. They grow continuously, so it gnaws on hard things to whittle them down.")
        mewtwo = Pokemon(name="Mewtwo", price=5000, type="Psychic", description="A POKéMON whose genetic code was repeatedly recombined for research. It turned vicious as a result.")
        db.session.add(admin)
        db.session.add(ratata)
        db.session.add(mewtwo)
        db.session.commit()
        with self.app:
            self.app.post('/login', data=dict(trainername="Admin", password='adminadmin'), follow_redirects=True)
        pass

    def tearDown(self):
        if current_user and current_user.is_authenticated:
            logout_user()
        db.session.remove()
        db.drop_all()

    # Ensuretrainer can see available Pokemon
    def test_trainer_see_pokemon(self):
        with self.app:
            response = self.app.get('/market',follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Ratata', response.data)
            self.assertIn(b'Mewtwo', response.data)

    # Ensure trainer can catch available Pokemon if has enough pokeballs (new trainer starts with 1000 pokeballs)
    def test_trainer_can_catch(self):
        with self.app:
            response = self.app.post('/market', data=dict(catched_pokemon='Ratata'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Congratulations! You caught Ratata for 100 PokeBalls', response.data)
            self.assertIn('/market', request.url)

    # Ensure trainer can't catch available Pokemon if doesn't have enough pokeballs
    def test_trainer_cannot_catch(self):
        with self.app:
            response = self.app.post('/market', data=dict(catched_pokemon='Mewtwo'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"You do not have enough PokeBalls to catch Mewtwo!", response.data)
            self.assertIn('/market', request.url)

    # Ensure trainer can sell one of his owned Pokemon
    def test_trainer_can_sell(self):
        with self.app:
            self.app.post('/market', data=dict(catched_pokemon='Ratata'), follow_redirects=True)
            response = self.app.post('/market', data=dict(sold_pokemon='Ratata'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Congratulations! You sold Ratata for 100 PokeBalls', response.data)
            self.assertIn('/market', request.url)

    # Ensure trainer can't sell Pokemon not owned by him
    def test_trainer_cannot_sell(self):
        with self.app:
            response = self.app.post('/market', data=dict(sold_pokemon='Mewtwo'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Something went wrong with selling Mewtwo!', response.data)
            self.assertIn('/market', request.url)

if __name__ == '__main__':
    unittest.main()
