"""
wraqStats account view.
URLs include:
/
"""
import flask
import wraqStats
import uuid
import hashlib
import pathlib
import os

# Helper Functions
def password_hasher(pass_original):
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + pass_original
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string

def login_helper():
    username = flask.request.form.get("username", None)
    password = flask.request.form.get("password", None)

    if username is None or password is None:
        flask.abort(400)
    
    # check authentication
    password_db_string = password_hasher(password)
    
    # connect to database
    connection = wraqStats.model.get_db()
    passwordCheck = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ? AND password = ?",
        (username, password_db_string, )
    )
    passwordCheck = passwordCheck.fetchall()
    if len(passwordCheck) == 0:
        flask.abort(403)
    
    # set session cookie
    flask.session['logname'] = passwordCheck[0]["username"]

def create_helper():
    username = flask.request.form.get("username", None)
    password = flask.request.form.get("password", None)
    fullname = flask.request.form.get("fullname", None)
    email = flask.request.form.get("email", None)
    fileobj = flask.request.files.get("file", None)

    if (username is None or password is None or fullname is None 
        or email is None or filename is None):
        flask.abort(400)
    
    filename = fileobj.filename

    connection = wraqStats.model.get_db()
    userCheck = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    if len(userCheck.fetchall()) != 0:
        flask.abort(409)
    
    password_db_string = password_hasher(password)

    # image processing
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    
    # TODO: Nathan Save Files to disk: user filename
    path = wraqStats.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    userCheck = connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password_db_string, )
    )

    # set session cookie
    flask.session['logname'] = username

def delete_helper():
    if 'logname' not in flask.session:
        flask.abort(403)

    # connect to database
    connection = wraqStats.model.get_db()
    deleteFiles = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ?",
        (flask.session['logname'], )
    )
    deleteFiles = deleteFiles.fetchall()

    # TODO: Nathan delete files (users posts) from disk
    for file in deleteFiles:
        path = wraqStats.app.config["UPLOAD_FOLDER"]/file["filename"]
        os.remove(path)

    deleteFiles = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'], )
    )
    deleteFiles = deleteFiles.fetchall()

    # TODO: Nathan delete files (user prof pic) from disk
    path = wraqStats.app.config["UPLOAD_FOLDER"]/deleteFiles[0]["filename"]
    os.remove(path)

    # removes correlated entries in the database
    deletion = connection.execute(
        "DELETE FROM users "
        "WHERE username = ?",
        (flask.session['logname'], )
    )

    # remove session
    flask.session.pop('logname', None)

def edit_helper():
    # check to see if user is logged in
    if 'logname' not in flask.session:
        flask.abort(403)
    
    fullname = flask.request.form.get("fullname", None)
    email = flask.request.form.get("email", None)

    if fullname is None or email is None:
        flask.abort(400)
    
    fileobj = flask.request.files.get("file", None)
    newImage = False
    filename = ""

    if fileobj is not None:
        newImage = True
        filename = fileobj.filename

    # connect to database
    connection = wraqStats.model.get_db()

    if newImage:
        # retreive and delete photo from filesystem
        deleteFiles = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (flask.session['logname'], )
        )
        deleteFiles = deleteFiles.fetchall()

        # TODO: Nathan delete file (user old pic)
        path = wraqStats.app.config["UPLOAD_FOLDER"]/deleteFiles[0]["filename"]
        os.remove(path)

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"

        # TODO: upload new file pls (new user pic)
        path = wraqStats.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        
        updateDB = connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ?"
            "WHERE username = ?",
            (fullname, email, uuid_basename, flask.session['logname'], )
        )
    else:
        # update fullname and email in DB
        updateDB = connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?",
            (fullname, email, flask.session['logname'], )
        )

def editpass_helper():
    # check to see if user is logged in
    if 'logname' not in flask.session:
        flask.abort(403)
    
    password = flask.request.form.get("password", None)
    new_password1 = flask.request.form.get("new_password1", None)
    new_password2 = flask.request.form.get("new_password2", None)

    if password is None or new_password1 is None or new_password2 is None:
        flask.abort(400)
    
    # verify current password 
    # connect to database
    connection = wraqStats.model.get_db()
    passCheck = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'], )
    )
    passCheck = passCheck.fetchall()
    # Error Check
    if len(passCheck) != 1:
        print("ERROR: SOMETHING IS WRONG, MORE THAT 1 USER IN DB")
    
    pass_db = passCheck[0]['password']
    pass_given = password_hasher(password)
    if pass_db != pass_given:
        flask.abort(403)
    
    if new_password1 != new_password2:
        flask.abort(401)
    
    new_pass_db = password_hasher(new_password1)

    updatePass = connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (new_pass_db, flask.session['logname'], )
    )

@wraqStats.app.route('/accounts/login/')
def acc_login():
    """Display /acounts/login/ route."""

    # Check to see if user is logged in
    if 'logname' in flask.session:
        flask.redirect(flask.url_for('show_index'))
    else:
        context = {}
        return flask.render_template("acclogin.html", **context)

@wraqStats.app.route('/accounts/create/')
def acc_create():
    """Display /acounts/login/ route."""

    # Check to see if user is logged in
    if 'logname' in flask.session:
        flask.redirect(flask.url_for('acc_edit'))

    context = {}
    return flask.render_template("acccreate.html", **context)

@wraqStats.app.route('/accounts/delete/')
def acc_delete():
    """Display /acounts/login/ route."""

    # TODO: Check to see if user is logged in

    context = {"logname": flask.session['logname']}
    return flask.render_template("accdelete.html", **context)

@wraqStats.app.route('/accounts/edit/')
def acc_edit():
    """Display /acounts/login/ route."""

    # TODO: Check to see if user is logged in
    connection = wraqStats.model.get_db()
    imgCheck = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (flask.session['logname'], )
    )
    imgCheck = imgCheck.fetchall()
    if len(imgCheck) != 1:
        print("ERROR: MORE THAT 1 USER W SAME USERNAME IN DB")
    context = {"logname": flask.session['logname'], "user_img_url": imgCheck[0]['filename']}
    return flask.render_template("accedit.html", **context)

@wraqStats.app.route('/accounts/password/')
def acc_password():
    """Display /acounts/login/ route."""

    # TODO: Check to see if user is logged in

    context = {"logname": flask.session['logname']}
    return flask.render_template("accpassword.html", **context)

@wraqStats.app.route('/accounts/', methods=['POST'])
def acc_postreq():
    queryParams = flask.request.args
    returnURL = queryParams.get("target")

    opType = flask.request.form["operation"]

    if opType == 'login':
        login_helper()
    elif opType == 'create':
        create_helper()
    elif opType == 'delete':
        delete_helper()
    elif opType == 'edit_account':
        edit_helper()
    elif opType == 'update_password':
        editpass_helper()
    
    # redirect to target URL
    return flask.redirect(returnURL, code=302)

@wraqStats.app.route('/accounts/logout/', methods=['POST'])
def acc_logout():
    # TODO: Check to see if user is logged in
    flask.session.pop('logname', None)
    return flask.redirect(flask.url_for('acc_login'), code=302)