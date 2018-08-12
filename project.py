# GENERAL IMPORTS
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
)
from sqlalchemy import create_engine, asc, exists
from sqlalchemy.orm import sessionmaker
from setup import Base, Item, Category, User
from flask import session as login_session
import random
import string

# IMPORTS FOR OAUTH
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///items.db?check_same_thread=False')
# Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Create user in Database if it doesn't already exist.
    user = session.query(User.id).filter_by(gid=gplus_id).scalar() is not None
    if user is False:
        newUser = User(
            gid=gplus_id,
            username=data['name'],
            picture=data['picture'],
            email=data['email']
        )
        session.add(newUser)
        session.commit()

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img class="login-success-image" src="'
    output += login_session['picture']
    output += ' "> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Revoke access from tokens, log user out of our application.
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/'
           'revoke?token=%s' % login_session['access_token'])
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # if the request was successful, we delete all session data.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template(
            'categories.html',
            categories=categories,
            user=login_session)
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs to view Category Information


@app.route('/category/<int:category_id>/item/JSON')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template(
        'categories.html',
        categories=categories,
        user=login_session)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        owner_id = session.query(
            User.id).filter_by(
            gid=login_session['gplus_id']).one()[0]
        newCategory = Category(name=request.form['name'], owner_id=owner_id)
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'newCategory.html',
            user=login_session,
            csrf=login_session['state'])

# Edit a category


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    user_id = session.query(User.id).filter_by(
        gid=login_session['gplus_id']).one()[0]
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if user_id != editedCategory.owner_id:
        # Check if user is allowed to access this resource
        flash("You are not allowed to edit this category.")
        return redirect(url_for('showCategories', category_id=category_id))
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template(
            'editCategory.html',
            category=editedCategory,
            user=login_session,
            csrf=login_session['state'])


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    user_id = session.query(User.id).filter_by(
        gid=login_session['gplus_id']).one()[0]
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if user_id != categoryToDelete.owner_id:
        # Check if user is allowed to access this resource
        flash("You are not allowed to delete this category.")
        return redirect(url_for('showCategories', category_id=category_id))
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template(
            'deleteCategory.html',
            category=categoryToDelete,
            user=login_session,
            csrf=login_session['state'])

# Show a category item


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def showItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    owner = session.query(User).filter_by(id=category.owner_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return render_template(
        'item.html',
        items=items,
        category=category,
        owner=owner,
        user=login_session)


# Create a new item item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    user_id = session.query(User.id).filter_by(
        gid=login_session['gplus_id']).one()[0]
    if category.owner_id != user_id:
        # Check if user is allowed to access this resource
        flash("You are not allowed to add items to this category.")
        return redirect(url_for('showItem', category_id=category_id))
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            category_id=category_id,
            owner_id=user_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template(
            'newItem.html',
            category_id=category_id,
            user=login_session,
            csrf=login_session['state'])

# Edit a item item


@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit',
    methods=[
        'GET',
        'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    user_id = session.query(User.id).filter_by(
        gid=login_session['gplus_id']).one()[0]
    if user_id != editedItem.owner_id:
        # Check if user is allowed to access this resource
        flash("You are not allowed to edit this item.")
        return redirect(url_for('showItem', category_id=category_id))
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('%s Successfully Edited' % request.form['name'])
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template(
            'editItem.html',
            category_id=category_id,
            item_id=item_id,
            item=editedItem,
            user=login_session,
            csrf=login_session['state'])


# Delete a item item
@app.route(
    '/category/<int:category_id>/item/<int:item_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    user_id = session.query(User.id).filter_by(
        gid=login_session['gplus_id']).one()[0]
    if user_id != itemToDelete.owner_id:
        # Check if user is allowed to access this resource
        flash("You are not allowed to delete this item.")
        return redirect(url_for('showItem', category_id=category_id))
    if request.method == 'POST':
        if request.form['csrf_token'] != login_session['state']:
            # Cross Site Request Forgery Protection
            flash('CSRF Token Invalid - Please log back in.')
            return redirect(url_for('showCategories'))
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template(
            'deleteItem.html',
            item=itemToDelete,
            category_id=category_id,
            user=login_session,
            csrf=login_session['state'])


if __name__ == '__main__':
    app.secret_key = '2831ss8wehf9h19h3hf9aha82e98ah9a'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
