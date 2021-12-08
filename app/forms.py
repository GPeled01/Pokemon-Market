from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import Trainer


class SignUpForm(FlaskForm):
    def validate_trainername(self, trainername_to_check):
        trainer = Trainer.query.filter_by(trainername=trainername_to_check.data).first()
        if trainer:
            raise ValidationError('Trainer name already exists! Please try a different name')

    def validate_email(self, email_to_check):
        email = Trainer.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email address already exists! Please try a different email address')

    trainername = TextField('Trainer Name:', validators=[DataRequired(), Length(min=2, max=25)])
    email = TextField('Email Address:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password')])


class LoginForm(FlaskForm):
    trainername = TextField(label='Trainer Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])


class CatchPokemonForm(FlaskForm):
    submit = SubmitField(label='Catch Pokemon')


class SellPokemonForm(FlaskForm):
    submit = SubmitField(label='Sell Pokemon')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password:', validators=[DataRequired()])
    new_password = PasswordField('New Password:', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField('Confirm New Password:', validators=[DataRequired(), EqualTo('new_password')])
