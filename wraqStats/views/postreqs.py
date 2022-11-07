"""
Insta485 index (main) view.
URLs include:
/
"""

import flask
import insta485
import uuid
import pathlib
import os
@insta485.app.route("/likes/", methods=['POST'])
def post_like():
    queryParams = flask.request.args
    returnURL = queryParams.get("target")

    logname = "awdeorio"

    opType = flask.request.form["operation"]
    postid = flask.request.form["postid"]

    # Connect to database
    connection = insta485.model.get_db()
    check = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid, )
    )
    if opType == 'unlike':
        # error check to see if logged in user has not liked post
        if len(check.fetchall()) == 0:
            flask.abort(409)
        
        # remove like
        deletion = connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, postid, )
        )
        
    elif opType == 'like':
        # error check to see if logged in user already liked post
        if len(check.fetchall()) != 0:
            flask.abort(409)
        
        # add like
        insertion = connection.execute(
            "INSERT INTO likes(owner, postid) "
            "VALUES (?, ?)",
            (logname, postid, )
        )

    else:
        print("Error")

    # print(opType)
    return flask.redirect(returnURL, code=302)

@insta485.app.route("/comments/", methods=['POST'])
def post_comment():
    connection = insta485.model.get_db()
    logname = "awdeorio"
    returnURL = flask.request.args
    returnURL = returnURL.get("target")
    opType = flask.request.form["operation"]
    if opType == "create":
        commentText = flask.request.form["text"]
        if commentText == "":
            flask.abort(400)
        postid = flask.request.form["postid"]
        put_comment = connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)",
            (logname, postid, commentText, )
        )
    else:
        commentid = flask.request.form["commentid"]
        find_comment = connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
        find_comment = find_comment.fetchall()
        if logname != find_comment[0]["owner"]:
            flask.abort(403)
        delete_comment = connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
    if returnURL == "":
        return flask.redirect("/")
    return flask.redirect(returnURL, code=302)

@insta485.app.route("/posts/", methods=['POST'])
def post_post():
    connection = insta485.model.get_db()
    logname = "awdeorio"
    returnURL = flask.request.args
    returnURL = returnURL.get("target")
    opType = flask.request.form["operation"]
    if opType == "create":
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        if filename == "":
            return flask.abort(400)
        # Compute base name (filename without directory).  We use a UUID to avoid
        # clashes with existing files, and ensure that the name is compatible with the
        # filesystem.
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        posting = connection.execute(
            "INSERT INTO posts(filename, owner) "
            "VALUES (?, ?)",
            (uuid_basename, logname, )
        )
    elif opType == "delete":
        postid = flask.request.form["postid"]
        delete_file = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE postid = ?",
            (postid, )
        )
        delete_db = connection.execute(
            "DELETE FROM posts "
            "WHERE postid = ?",
            (postid, )
        )
        delete_file = delete_file.fetchall()
        path = insta485.app.config["UPLOAD_FOLDER"]/delete_file[0]["filename"]
        os.remove(path)

    if returnURL == "":
        return flask.redirect("/users/" + logname, code=302)
    
    return flask.redirect(returnURL, code=302)

@insta485.app.route("/following/", methods=['POST'])
def follow_request():
    queryParams = flask.request.args
    returnURL = queryParams.get("target")

    logname = "awdeorio"

    opType = flask.request.form["operation"]
    username = flask.request.form["username"]

    # Connect to database
    connection = insta485.model.get_db()
    check = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username, )
    )

    if opType == 'follow':
        # error check to see if logged in user already follows user
        if len(check.fetchall()) != 0:
            flask.abort(409)
        
        # follow user
        followPerson = connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES (?, ?)",
            (logname, username, )
        )
    elif opType == 'unfollow':
        # error check to see if logged in user does not already follow user
        if len(check.fetchall()) == 0:
            flask.abort(409)
        
        # unfollow user
        unFollowPerson = connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, username, )
        )
    else:
        print("Error")

    print(opType)
    print(returnURL)
    return flask.redirect(returnURL, code=302)