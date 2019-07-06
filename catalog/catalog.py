# !/usr/bin/env python3
from flask import (
    Flask,
    flash,
    render_template,
    request,
    url_for,
    redirect,
    jsonify
    )
from flask import session as login_session
from flask import make_response

# Importing sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os
import random
import string
import httplib2
import json
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
    )
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dbsetup import Base, Mobile_Category, Menu_Items, Login_User

app = Flask(__name__)

engine = create_engine('sqlite:///mobile.db')
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))

client_file = open("client_secrets.json")
CLIENT_ID = json.loads(client_file.read())['web']["client_id"]
client_file.close()


@app.route('/')
@app.route('/category/')
def home():
    """Home page for the website"""
    All_Items = session.query(Menu_Items).all()
    return render_template(
        'showitems.html',
        Items=All_Items, hasRecent=True, category_id=None)


@app.route('/category/items.json')
def json_Items():
    """gives the json data"""
    mobiles = session.query(Menu_Items).all()
    return jsonify(mobiles=[mobile.serialise for mobile in mobiles])


@app.route('/category/<int:categoryid>/items.json')
def json_Items_Category(categoryid):
    """ gives the json data for single item """
    mobiles = session.query(Menu_Items).filter_by(
        mobile_category_id=categoryid).all()
    return jsonify(mobiles=[mobile.serialise for mobile in mobiles])


@app.route("/category/add", methods=['GET', 'POST'])
def Add_Category():
    """To create new category"""
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if not admin:
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('category.html')
    elif request.method == 'POST':
        cat_name = request.form['Cname']
        if cat_name:
            catObj = Mobile_Category(name=cat_name, id_user=admin.id)
            session.add(catObj)
            session.commit()
            flash('your Item is added', 'success')
        return redirect(url_for('home'))
    else:
        flash('Category not added successfully', 'danger')
        return redirect(url_for('home'))


@app.route('/category/<int:category_id>/menu/')
def Show_Category_Items(category_id):
    """Display categories list"""
    if request.method == 'GET':
        items = session.query(Menu_Items).filter_by(
            mobile_category_id=category_id)
    return render_template(
        'showitems.html', Items=items, hasRecent=False, category_id=category_id
        )


@app.route('/category/<int:category_id>/edit/', methods=["GET", "POST"])
def Edit_Category(category_id):
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if admin == 'None':
        flash("Invalid user")
        return redirect(url_for('home'))
    category = session.query(Mobile_Category).filter_by(
        id=category_id).one_or_none()
    if not category:
        flash("category not found", 'danger')
        return redirect(url_for('home'))
    if category.id_user != admin.id:
        flash("Your are not admin", "danger")
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('editcategory.html', category=category)
    else:
        new_category_name = request.form['category_name']
        category.name = new_category_name
        session.add(category)
        session.commit()
        flash("Updated Successfully", 'success')
        return redirect(url_for('home'))


# to  delete the category
@app.route('/category/<int:category_id>/delete')
def Delete_Category(category_id):

    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if admin == 'None':
        flash("Invalid user")
        return redirect(url_for('home'))
    category = session.query(Mobile_Category).filter_by(
        id=category_id).one_or_none()
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('home'))
    if category.id_user != admin.id:
        flash("Your are not admin", "danger")
        return redirect(url_for('home'))
    cname = category.name
    session.delete(category)
    session.commit()
    flash('deleted successfully '+str(cname), 'success')
    return redirect(url_for('home'))


@app.route("/category/<int:category_id>/menu/add", methods=['GET', 'POST'])
def Add_Mobile(category_id):
    # to add new item into the category
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))

    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if admin == 'None':
        flash("Invalid user")
        return redirect(url_for('home'))

    categoryname = session.query(Mobile_Category).filter_by(
        id=category_id).one_or_none()
    if not categoryname:
        flash('Category not found')
        return redirect(url_for('home'))

    login_admin_id = admin.id
    admin_id = categoryname.id_user
    if login_admin_id != admin_id:
        flash('your not correct person')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('menu_add.html', category_id=category_id)
    elif request.method == 'POST':
        mname = request.form['mname']
        des = request.form['desc']
        mprice = request.form['price']
        brand = request.form['brand']
        image = request.form['url']
        if mname:
            mObj = Menu_Items(
                name=mname,
                description=des,
                price=mprice,
                brand=brand,
                image=image,
                mobile_category_id=category_id
                )
            session.add(mObj)
            session.commit()
            flash('your item added', 'success')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/category/<int:category_id>/menu/<int:item_id>/details/')
def Show_Mobile_Details(category_id, item_id):
    item = session.query(Menu_Items).filter_by(
        mobile_category_id=category_id, id=item_id).one_or_none()
    if(not item):
        flash('item not available', 'danger')
        return redirect(url_for('home'))
    return render_template('itemInfo.html', item=item)


@app.route(
    '/category/<int:category_id>/menu/<int:item_id>/edit/',
    methods=["GET", "POST"]
    )
def Edit_Mobile(category_id, item_id):
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if admin == 'None':
        flash("Invalid user")
        return redirect(url_for('home'))

    item = session.query(Menu_Items).filter_by(
        mobile_category_id=category_id, id=item_id).one_or_none()
    if(not item):
        flash('item not available', 'danger')
        return redirect(url_for('home'))
    login_admin_id = admin.id
    admin_id = item.Mobile_Category.id_user
    if login_admin_id != admin_id:
        flash('your not correct person')
        return redirect(url_for('home'))
    if request.method == "GET":
        return render_template('edititem.html', item=item)
    else:
        name = request.form['m_name']
        description = request.form['desc']
        price = request.form['price']
        brand = request.form['brand']
        image = request.form['url']
        item.name = name
        item.description = description
        item.price = price
        item.brand = brand
        item.image = image
        session.add(item)
        session.commit()
        flash('Item details updated successfully', 'success')
        return redirect(
            url_for(
                'Show_Mobile_Details', category_id=category_id, item_id=item_id
                )
            )


@app.route('/category/<int:category_id>/menu/<int:item_id>/delete/')
def Delete_Mobile(category_id, item_id):
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Login_User).filter_by(
        gmail=login_session['email']).one_or_none()
    if admin == 'None':
        flash("Invalid user")
        return redirect(url_for('home'))

    item = session.query(Menu_Items).filter_by(
        mobile_category_id=category_id, id=item_id).one_or_none()
    if(not item):
        flash('item not available', 'danger')
        return redirect(url_for('home'))
    login_admin_id = admin.id
    admin_id = item.Mobile_Category.id_user
    if login_admin_id != admin_id:
        flash('you are not the admin', 'danger')
        return redirect(url_for('home'))
    session.delete(item)
    session.commit()
    flash("item removed successfully", 'danger')
    return redirect(url_for('home'))


# For Logout
@app.route('/logout')
def logout():
    if 'email' in login_session:
        flash('you logged out')
        return gdisconnect()
    flash('You are already logout.')
    return redirect(url_for('login'))

# login routing


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# it helps the user to loggedin and display flash profile


# GConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')

    # Obtain authorization code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("""Failed to upgrade the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token
        )
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    user_data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['email'] = user_data['email']
    login_session['provider'] = 'google'

    login_user_id = get_user_id(login_session['email'])
    if not login_user_id:
        login_user_id = Create_User(login_session)
    login_session['login_user_id'] = login_user_id
    flash("Welcome to your soap Marketing", "success")
    return "login successful "


def Create_User(login_session):
    print('\n'*5, 'create user start')
    email = login_session['email']
    print('\n'*5, email, '\n'*5)
    newUser = Login_User(gmail=email)
    session.add(newUser)
    session.commit()
    user = session.query(Login_User).filter_by(gmail=email).first()
    return user.id


def get_user_id(gmail):
    try:
        userlogin = session.query(Login_User).filter_by(gmail=gmail).one()
        return userlogin.id
    except Exception as e:
        return None


# Gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    del login_session['email']
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401
            )
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        response = redirect(url_for('home'))
        response.headers['Content-Type'] = 'application/json'
        flash("successfully Logout from your website", "success")
        return response
    else:
        # if given token is invalid, unable to revoke token
        response = make_response(
                json.dumps('Failed to revoke token for user'), 200
                )
        response.headers['Content-Type'] = 'application/json'
        return response


@app.context_processor
def inject_all():
    category = session.query(Mobile_Category).all()
    return dict(mycategories=category)


if __name__ == "__main__":
    app.debug = True
    app.secret_key = "hgdskajhgf"
    app.run(host='localhost', port=5000)
