"""
wraqStats index (main) view.
URLs include:
/
"""
import flask
import arrow
import wraqStats
@wraqStats.app.route('/')
def show_index():
    """Display / route."""

    # Connect to database
    connection = wraqStats.model.get_db()

    logname = "awdeorio"
    
    # Query database
    # cur = connection.execute(
    #     "SELECT username2 "
    #     "FROM following "
    #     "WHERE username1 = ?",
    #     (logname, )
    # )

    # user_posts = [logname]
    # for row in cur:
    #     user_posts.append(row['username2'])
    # print(user_posts)

    # testLike = connection.execute(
    #     "SELECT postid, COUNT(*) AS numLike "
    #     "FROM likes "
    #     "GROUP BY postid "
    # )
    # print(testLike.fetchall())
    # "WITH likeTable AS ( "
    #         "SELECT postid, COUNT(*) AS numLike "
    #         "FROM likes "
    #         "GROUP BY postid "
    #         ") "

    # Query Database: postid, owner, owner_img_url, img_url, timestamp, likes
    # Databases UsedL posts, following, likes
    posts = connection.execute(
            "SELECT posts.postid, posts.owner, users.filename AS owner_img_url, posts.filename AS img_url, posts.created AS timestamp "
            "FROM posts "
            "INNER JOIN users on posts.owner = users.username "
            "WHERE posts.owner IN ( "
                "SELECT username2 "
                "FROM following "
                "WHERE username1 = ? "
                ") "
            "OR posts.owner = ? "
            "ORDER BY posts.postid DESC",
        (logname, logname, )
    )
    posts = posts.fetchall()

    for p in posts:
        # Query Database: commendid, owner, text
        getComment = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY commentid",
            (p["postid"], )
        )
        getComment = getComment.fetchall()
        p["comments"] = getComment

        p["timestamp"] = arrow.get(p["timestamp"]).humanize(arrow.utcnow())

        checkLikes = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ? AND owner = ? ",
            (p["postid"], logname, )
        )
        if len(checkLikes.fetchall()) == 0:
            p["userHasLiked"] = False
        else:
            p["userHasLiked"] = True
        
        checkLikes = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ?",
            (p["postid"], )
        )
        p["likes"] = len(checkLikes.fetchall())
    # print(testLike.fetchall())

    print(posts)
    
    
    # users = cur.fetchall() # [{'username2': 'jflinn'}, {'username2': 'michjc'}]
    # print(users)
    
        
    # cur = connection.execute(
    #     "SELECT postid, owner, filename, filename, created, fullname "
    #     "FROM posts"
    #     "INNER JOIN users on users.username = posts.owner"
    #     "WHERE username != ?",
    #     (logname, )
    # )
    # print(users)

    # Add database info to context
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)

@wraqStats.app.route('/uploads/<img_url>')
def get_photo(img_url):
    return flask.send_from_directory(wraqStats.app.config['UPLOAD_FOLDER'], img_url)
