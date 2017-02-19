"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        if self.total_played > 0:
            return float(self.wins) / float(self.total_played)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        win_percentage=self.win_percentage)

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.update_stats()

    def update_stats(self):
        """Update game stats"""
        self.total_played += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    next_move_by = ndb.StringProperty()
    target = ndb.PickleProperty(repeated=True)
    attempts_remaining = ndb.IntegerProperty(required=True)
    number_of_correct = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user, words):
        """Creates and returns a new game"""

        game = Game(user=user,
                    next_move_by='',
                    attempts_remaining=7,
                    number_of_correct=0,
                    game_over=False,
                    history=['']
                    )
        if len(words.split()) - 1 > 0:
            game.target = list(
                words.split()[random.choice(range(0, len(words.split()) - 1))]),
        else:
            game.target = list(words.split()[0])
        game.put()
        return game

    def to_form(self, message):
        """Copies a Game state info to a Game form"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        user=self.user.get().name,
                        next_move_by=self.next_move_by,
                        attempts_remaining=self.attempts_remaining,
                        number_of_correct=self.number_of_correct,
                        game_over=self.game_over,
                        message=message,
                        history=self.history)
        return form

    def end_game(self, won=False):
        """End game"""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.number_of_correct + 7 - self.attempts_remaining)

        score.put()


class GameForm(messages.Message):
    """Game form"""
    urlsafe_key = messages.StringField(1, required=True)
    user = messages.StringField(2, required=True)
    next_move_by = messages.StringField(3)
    attempts_remaining = messages.IntegerField(4, required=True)
    number_of_correct = messages.IntegerField(5, required=True)
    game_over = messages.BooleanField(6, required=True)
    message = messages.StringField(7)
    history = messages.StringField(8, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    words = messages.StringField(2, required=True)


class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty()

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         won=self.won,
                         date=str(self.date),
                         guesses=self.guesses)


class ScoreForm(messages.Message):
    """Score information for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4)


class ScoreForms(messages.Message):
    """Container for multiple ScoreForm"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user = messages.StringField(1, required=True)
    guess = messages.StringField(2, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)
