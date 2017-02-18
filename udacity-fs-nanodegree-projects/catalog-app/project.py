#Import flask libraries
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

#Import sqlalchemy libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

#OAuth imports
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#Get client_id from client_secrets file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

#Create your database sessions
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Making an API Endpoint for categories
@app.route('/categories/<int:category_id>/item/JSON')
def categoryJSON(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return jsonify(CategoryItems = [i.serialize for i in items])

#Making an API Endpoint for Items in a category
@app.route('/categories/<int:category_id>/item/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item = item.serialize)

#Routing to login
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

#Use google plus signup
@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
   
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
   
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
   
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    print params
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #Add user if it's not already in the user database
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output

#Google plus signout
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('credentials')
   
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	login_session.clear()
    	response = make_response(json.dumps('Successfully logged out.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return redirect(url_for('index'))
    else:
	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

#Routing to the main page
@app.route('/')
def index():
    categories = session.query(Category).all()
    latest = session.query(Item, Category).filter(Category.id == Item.category_id).order_by(Item.id).limit(5).all()
    return render_template('index.html', categories = categories, latest = latest)

#List of categories after login
@app.route('/categories')
def category():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    latest = session.query(Item, Category).filter(Category.id == Item.category_id).order_by(Item.id).limit(5).all()    
    user = login_session['username']
    return render_template('categories.html', categories = categories, user = user, latest = latest)

#List of items
@app.route('/categories/<int:category_id>/')
def category_item(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id)
    user = login_session['username']
    return render_template('categoryitem.html', category=category, items=items, user = user)

#Create new category
@app.route('/categories/new', methods = ['GET', 'POST'])
def add_new_category():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    user = login_session['username']
    user_id = get_user_id(login_session['email'])
    
    if request.method == 'POST':
        if user_id == None:
            user_id = create_user(login_session)
        if request.form['name']:
            newCategory = Category(name = request.form['name'], user_id = user_id)
            session.add(newCategory)
            session.commit()
            return redirect(url_for('category', categories = categories))
    else:
        return render_template('addcategory.html',user = user)

#Create route for new category item
@app.route('/categories/<int:category_id>/new', methods = ['GET', 'POST'])
def new_category_item(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(id = category_id).one()
    if category.user_id != get_user_id(login_session['email']):
        return "<script>function userAlert(){alert('You are not authorized to create new item in this category. Please choose a category you created and add new item!');}</script><body onload='userAlert()''>"
    user = login_session['username']
    user_id = get_user_id(login_session['email'])
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], category_id = category_id, description = request.form['description'], user_id = user_id)
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('category_item', category_id = category_id))
    else:
        return render_template('newitem.html', category_id = category_id, category = category, user = user)

#Edit route for new category item
@app.route('/categories/<int:category_id>/<int:item_id>/edit', methods = ['GET', 'POST'])
def edit_category_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    
    editedItem = session.query(Item).filter_by(id = item_id).one()
    if editedItem.user_id != get_user_id(login_session['email']):
        return "<script>function userAlert(){alert('You are not authorized to edit this item. Please choose an item you created!');}</script><body onload='userAlert()''>"
 
    user = login_session['username']
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            if request.form['description']:
                            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item %s is edited!" % editedItem.name)
        return redirect(url_for('category_item', category_id = category_id))
    else:
        return render_template('itemedit.html', category_id = category_id, item_id = item_id, i = editedItem, user = user)
    
#Delete route for new category item
@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods = ['GET', 'POST'])
def delete_category_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(Item).filter_by(id = item_id).one()
   
    if deletedItem.user_id != get_user_id(login_session['email']):
        return "<script>function userAlert(){alert('You are not authorized to delete this item. Please choose an item you created!');}</script><body onload='userAlert()''>"

    user = login_session['username']
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Item %s is deleted!" % deletedItem.name)
        return redirect(url_for('category_item', category_id = category_id))
    else:
        return render_template('itemdelete.html', category_id = category_id, item_id = item_id, i = deletedItem, user = user)

#Get user_id (id in database) of a user
def get_user_id(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None
    
#Get user info
def get_user_info(user_id):
    user = session.query(User).filter_by(user_id = user_id).one()
    return user

#Create user in User 
def create_user(login_session):

    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secrete_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
