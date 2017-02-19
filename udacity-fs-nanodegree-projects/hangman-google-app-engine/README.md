#Full Stack Nanodegree Project 4: Hangman Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting your local server's address (by default localhost:8080.
 
 
##Game Description:
Hangman is a simple one player game. Game instructions are available
[here](https://en.wikipedia.org/wiki/Hangman_(game)).


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, wordlist
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game with the list of words provided. The list of words should be provided with each word separated by space.     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a guess which is a letter and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created, Along with, all the game history will be recorded.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
   - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage. 
    - Description: Returns all the history of the game with the given urlsafe_game_key. Each entry consists of guess and whether the player won or lost each time.
    
   - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage. 
    - Description: Cancels a game started.

   - **get_user_ranking**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: none
    - Returns: UserForms. 
    - Description: Ranks all players by percentage won.
    
    - **get_high_score**
    - Path: 'scores/leadersboard'
    - Method: GET
    - Parameters: rank_depth
    - Returns: UserForms. 
    - Description: Gets top n players based on wins.
    
     - **get_average_attempts**
    - Path: 'scores/leadersboard'
    - Method: GET
    - Parameters: none
    - Returns: UserForms. 
    - Description: Get the cached average moves remaining.

  
##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    - Also keeps track of wins and total_played.
    
 - **Game**
    - Stores unique game states. Associated with User models via KeyProperties
    user.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty as
    well.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, 
    user, attempts_remaining, number_of_correct, message, game_over, history).
 - **NewGameForm**
    - Used to create a new game (user_name, words)
 - **MakeMoveForm**
    - Inbound make move form (user, guess).
 - **ScoreForm**
    - Representation of a completed game's Score (date, won, guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserForm**
    - Representation of User. Includes winning percentage
 - **UserForms**
    - Container for one or more UserForm.
 - **StringMessage**
    - General purpose String container.
    
    
##Design Decisions
- I added a field to store the target in Game. The target is a word. I used PickleProperty because it allowed
me to store the word with all letters as members of a Python List in the datastore which seemed like the simplest way
and use later for checking membership of the guess letter by the player. It also help me to avoid the issue of checking repeated letters with the same guess letter provided by the player.
- I store history as a combination of guess and message in a list. That makes it easy to append.
- I used a 'game_over' flag as well to mark completed games.
- I used a check to make sure that the player enters a letter.

