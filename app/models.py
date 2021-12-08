from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import date


@login_manager.user_loader
def load_user(user_id):
    return Trainer.query.get(int(user_id))


trainersPokemon = db.Table('trainersPokemon',
                           db.Column('trainer_id', db.Integer, db.ForeignKey('trainer.id')),
                           db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id'))
                           )


class Trainer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    trainername = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password_hash = db.Column(db.String(70), nullable=False)
    pokeballs = db.Column(db.Integer, nullable=False, default=1000)
    pokemon = db.relationship('Pokemon', secondary=trainersPokemon,
                              backref=db.backref('owned_trainers', lazy='dynamic'))

    def __repr__(self):
        return f'Trainer {self.trainername}'

    @property
    def pokeballsWithComma(self):
        if len(str(self.pokeballs)) >= 4:
            return str(self.pokeballs)[:-3] + ',' + str(self.pokeballs)[-3:]
        else:
            return str(self.pokeballs)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plainTextPassword):
        self.password_hash = bcrypt.generate_password_hash(plainTextPassword).decode('utf-8')

    def checkPassword(self, attemptedPassword):
        return bcrypt.check_password_hash(self.password_hash, attemptedPassword)

    def canCatch(self, pokemonObj):
        return self.pokeballs >= pokemonObj.price

    def canSell(self, pokemonObj):
        return pokemonObj in self.pokemon


class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'Pokemon {self.name}'

    def catch(self, trainer):
        self.owned_trainers.append(trainer)
        trainer.pokeballs -= self.price
        db.session.commit()

    def sell(self, trainer):
        self.owned_trainers.remove(trainer)
        trainer.pokeballs += self.price
        db.session.commit()

    def numOfTrainers(self):
        return len(list(self.owned_trainers))
