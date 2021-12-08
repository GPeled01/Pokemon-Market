from flask import request, render_template, flash, redirect, url_for
from app import app, db, models
from .models import Pokemon, Trainer
from .forms import SignUpForm, LoginForm, CatchPokemonForm, SellPokemonForm, ChangePasswordForm
from flask_login import login_user, logout_user, login_required, current_user
import json
import logging
from flask.logging import default_handler

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)


@app.route('/')
@app.route('/home')
def home():
    app.logger.info('Entered home page')
    return render_template('home.html', title='Pokemon Market')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market():
    app.logger.info('Entered market page')
    catchForm = CatchPokemonForm()
    sellForm = SellPokemonForm()

    if request.method == "POST":
        # Catch Pokemon logic
        catchedPokemon = request.form.get('catched_pokemon')
        catchedPokemonObj = Pokemon.query.filter_by(name=catchedPokemon).first()
        if catchedPokemonObj:
            if current_user.canCatch(catchedPokemonObj):
                catchedPokemonObj.catch(current_user)
                app.logger.info(
                    f"{current_user.trainername} catched {catchedPokemonObj.name} for {catchedPokemonObj.price} PokeBalls")
                flash(f"Congratulations! You caught {catchedPokemonObj.name} for {catchedPokemonObj.price} PokeBalls",
                      category='success')
            else:
                app.logger.warning(
                    f"{current_user.trainername} tried to catch {catchedPokemonObj.name} for {catchedPokemonObj.price} PokeBalls but failed (not enough pokeballs)")
                flash(f"You do not have enough PokeBalls to catch {catchedPokemonObj.name}!", category='danger')

        # Sell Pokemon logic
        soldPokemon = request.form.get('sold_pokemon')
        soldPokemonObj = Pokemon.query.filter_by(name=soldPokemon).first()
        if soldPokemonObj:
            if current_user.canSell(soldPokemonObj):
                soldPokemonObj.sell(current_user)
                app.logger.info(
                    f"{current_user.trainername} sold {catchedPokemonObj.name} for {catchedPokemonObj.price} PokeBalls")
                flash(f"Congratulations! You sold {soldPokemonObj.name} for {soldPokemonObj.price} PokeBalls",
                      category='success')
            else:
                app.logger.warning(
                    f"{current_user.trainername} tried to sell {catchedPokemonObj.name} but failed (does not own this Pokemon)")
                flash(f"Something went wrong with selling {soldPokemonObj.name}!", category='danger')

        return redirect(url_for('market'))

    if request.method == "GET":
        pokemon = Pokemon.query.all()
        ownedPokemon = current_user.pokemon
        return render_template('market.html', title='Market', pokemon=pokemon, catchForm=catchForm, sellForm=sellForm,
                               ownedPokemon=ownedPokemon)


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    app.logger.info('Entered sign up page')
    form = SignUpForm()
    if form.validate_on_submit():
        trainername = form.trainername.data
        email = form.email.data
        password = form.password.data
        newTrainer = Trainer(trainername=trainername, email=email, password=password)
        db.session.add(newTrainer)
        db.session.commit()
        login_user(newTrainer)
        app.logger.info(f"{newTrainer.trainername} succeccfully created an account")
        flash(f'Trainer account created! You are now logged in as: {newTrainer.trainername}', category='success')
        return redirect(url_for('market'))
        if form.errors:  # If there are validation errors
            for err_msg in form.errors.values():
                app.logger.warning(f"Some validation errors occurred while {trainername} tried to create an account")
                flash(f'An error occurred while trying to create an account.', category='danger')
    return render_template('sign_up.html', title='Create Trainer Account', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info('Entered login page')
    form = LoginForm()
    if form.validate_on_submit():
        trainername = form.trainername.data
        password = form.password.data
        attemptedTrainer = Trainer.query.filter_by(trainername=trainername).first()
        if attemptedTrainer and attemptedTrainer.checkPassword(attemptedPassword=password):
            login_user(attemptedTrainer)
            app.logger.info(f"{attemptedTrainer.trainername} succeccfully logged in")
            flash(f'Successfully logged in as: {attemptedTrainer.trainername}', category='success')
            return redirect(url_for('market'))
        else:
            app.logger.warning(f"{trainername} failed to login (password do not match)")
            flash('Trainer name and password do not match! Please try again', category='danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    app.logger.info('Entered logout page')
    trainername = current_user.trainername
    logout_user()
    app.logger.info(f"{trainername} succeccfully logged out")
    flash("Successfully logged out!", category='info')
    return redirect(url_for('home'))


@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    trainername = current_user.trainername
    app.logger.warning(f"{trainername} is trying to change password")
    form = ChangePasswordForm()
    if form.validate_on_submit():
        oldPassword = form.old_password.data
        changeTrainer = Trainer.query.filter_by(id=current_user.id).first()
        if changeTrainer and changeTrainer.checkPassword(attemptedPassword=oldPassword):
            changeTrainer.password = form.new_password.data
            db.session.commit()
            logout_user()
            app.logger.warning(f"{trainername} changed password")
            flash(f'Your password have been changed successfully.', category='success')
            return redirect(url_for('login'))
        else:
            app.logger.warning(f"{trainername} failed to login (old password do not match)")
            flash('Old password does not match! Please try again', category='danger')
        if form.errors:  # If there are validation errors
            for err_msg in form.errors.values():
                app.logger.warning(f"Some validation errors occurred while {trainername} tried to change password")
                flash(f'An error occurred while trying to change password.', category='danger')
    return render_template('change_password.html', title='Change Password', form=form)


@app.route('/review', methods=['POST'])
def review():
    data = json.loads(request.data)
    pokemonId = int(data.get('pokemon_id'))
    pokemon = Pokemon.query.get(pokemonId)

    if data.get('review_type') == "like":
        pokemon.likes += 1
    else:
        pokemon.dislikes += 1

    db.session.commit()
    app.logger.info(f"Review for {pokemon.name} was succeccfully processed by {current_user.trainername}")
    return json.dumps({'status': 'OK', 'likes': pokemon.likes, 'dislikes': pokemon.dislikes})
