import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, UserForm, UserForms
from utils import get_by_urlsafe


CREATE_USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                                  email=messages.StringField(2))
CREATE_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm, urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1), email=messages.StringField(2))
TOP_RANK_REQUEST = endpoints.ResourceContainer(
    rank_depth=messages.IntegerField(1))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='hangman', version='v1')
class HangManApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=CREATE_USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A user with that name already exists!')
        if User.query(User.email == request.email).get():
            raise endpoints.ConflictException(
                'A user with that email address already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} is created!'.format(request.user_name))

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their win percentage"""
        users = User.query(User.total_played > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=CREATE_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Create new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'One or more of the users with the provided name does not exist')
        try:
            game = Game.new_game(user.key, request.words)
        except ValueError:
            raise endpoints.BadRequestExcception
        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')

        return game.to_form('Good luck playing hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='get/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to take a move!')
        else:
            raise endpoints.NotFoundExeption('Game not found!')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(Game.user == user.key).\
            filter(Game.game_over is False)
        return GameForms(items=[game.to_form('Games for user: ' + str(User.name)) for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Delete a game. Game must not have ended to be deleted"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found')

        if game.game_over:
            game.next_move_by = request.user
            return game.to_form('Game already over!')
        if game.attempts_remaining < 1 and game.number_of_correct != len(game.target):
            game.end_game(False)
            msg = 'Game over!'
            move = request.guess + ',' + msg
            game.history.append(move)
            game.next_move_by = request.user
            user = User.query(User.name == request.user).get()
            return game.to_form(msg)

        if (game.attempts_remaining >= 1 and list(request.guess) == game.target):
            game.end_game(True)
            game.attempts_remaining = 0
            game.number_of_correct = len(game.target)
            msg = 'You won!'
            move = request.guess + ',' + msg
            game.history.append(move)
            game.next_move_by = request.user
            user = User.query(User.name == request.user).get()
            user.add_win()
            return game.to_form(msg)

        if game.attempts_remaining >= 1 and request.guess.lower() in game.target:
            game.number_of_correct += 1
            game.target[game.target.index(request.guess)] = ''
            msg = 'You got it!'
            if (game.number_of_correct == len(game.target)):
                game.end_game(True)
                game.attempts_remaining = 0
                game.number_of_correct = len(game.target)
                msg = 'You won!'
                move = request.guess + ',' + msg
                game.history.append(move)
                game.next_move_by = request.user
                user = User.query(User.name == request.user).get()
                user.add_win()
                game.put()
                return game.to_form(msg)

            move = request.guess + ',' + msg
            game.history.append(move)
            game.next_move_by = request.user
            game.put()
            return game.to_form(msg)

        if game.attempts_remaining >= 1 and request.guess.lower() not in game.target:
            game.attempts_remaining -= 1
            msg = 'You lost!'
            move = request.guess + ',' + msg
            game.history.append(move)
            game.next_move_by = request.user
            game.put()
            return game.to_form('You lost!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=TOP_RANK_REQUEST,
                      response_message=UserForms,
                      path='scores/leadersboard',
                      name='high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return all Users ranked by their win"""
        users = User.query(User.total_played > 0).fetch()
        users = sorted(users, key=lambda x: x.wins, reverse=True)
        users = users[0:request.rank_depth]
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over is False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                            for game in games])
            average = float(total_attempts_remaining) / count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([HangManApi])
