"""
wraqStats user (main) view.
URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/followers/
/users/<user_url_slug>/following/
"""
import flask
import arrow
import wraqStats

@wraqStats.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Display /users/<user_url_slug>/followers/ route."""

    # Connect to database
    connection = wraqStats.model.get_db()

    logname = "awdeorio"
    fullname = ""

    # get username
    counts = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    counts = counts.fetchall()

    # Error Check: user does not exist
    if len(counts) == 0:
        flask.abort(404)
    
    for c in counts: # theoretically runs only one time if user exists
        fullname = c['fullname']
    
    # Query database to handle user posts
    userPosts = connection.execute(
        "SELECT postid, filename AS img_url "
        "FROM posts "
        "WHERE owner = ? "
        "ORDER BY postid DESC",
        (user_url_slug, )
    )
    userPosts = userPosts.fetchall()

    # print(followers)

    # Add database info to context
    context = {"logname": logname, "username": user_url_slug, "fullname": fullname, "total_posts": len(userPosts), "posts": userPosts}

    # get number of followers
    counts = connection.execute(
        "SELECT following.username1 AS username "
        "FROM following "
        "WHERE following.username2 = ? ",
        (user_url_slug, )
    )
    context["followers"] = len(counts.fetchall())

    # get number of following
    counts = connection.execute(
        "SELECT following.username2 AS username "
        "FROM following "
        "WHERE following.username1 = ? ",
        (user_url_slug, )
    )
    context["following"] = len(counts.fetchall())

    # check to see if logname followers user
    counts = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, user_url_slug, )
    )
    if len(counts.fetchall()) == 0:
        context['logname_follows_username'] = False
    else:
        context['logname_follows_username'] = True
    
    print(context)

    return flask.render_template("user.html", **context)

@wraqStats.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Display /users/<user_url_slug>/followers/ route."""

    # Connect to database
    connection = wraqStats.model.get_db()

    logname = "awdeorio"

    # get username
    counts = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    counts = counts.fetchall()

    # Error Check: user does not exist
    if len(counts) == 0:
        flask.abort(404)
    
    # Query database
    followers = connection.execute(
        "SELECT following.username1 AS username, users.filename AS user_img_url "
        "FROM following "
        "INNER JOIN users on following.username1 = users.username "
        "WHERE following.username2 = ? ",
        (user_url_slug, )
    )
    followers = followers.fetchall()

    for f in followers:
        # check to see if logname followers user
        lognameFollow = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, f['username'], )
        )
        if len(lognameFollow.fetchall()) == 0:
            f['logname_follows_username'] = False
        else:
            f['logname_follows_username'] = True

    # print(followers)

    # Add database info to context
    context = {"logname": logname, "followers": followers}
    return flask.render_template("followers.html", **context)

@wraqStats.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Display /users/<user_url_slug>/following/ route."""

    # Connect to database
    connection = wraqStats.model.get_db()

    logname = "awdeorio"

    # get username
    counts = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    counts = counts.fetchall()

    # Error Check: user does not exist
    if len(counts) == 0:
        flask.abort(404)
    
    # Query database
    following = connection.execute(
        "SELECT following.username2 AS username, users.filename AS user_img_url "
        "FROM following "
        "INNER JOIN users on following.username2 = users.username "
        "WHERE following.username1 = ? ",
        (user_url_slug, )
    )
    following = following.fetchall()

    for f in following:
        # check to see if logname followers user
        lognameFollow = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, f['username'], )
        )
        if len(lognameFollow.fetchall()) == 0:
            f['logname_follows_username'] = False
        else:
            f['logname_follows_username'] = True

    # print(following)

    # Add database info to context
    context = {"logname": logname, "following": following}
    return flask.render_template("following.html", **context)