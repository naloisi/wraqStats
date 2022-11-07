"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import arrow
@insta485.app.route("/posts/<postid_url_slug>/")
def show_posts(postid_url_slug):
    """Display posts route."""
    # Need: logname, owner (of the post), owner_img_url, postid, img_url,
    # timestamp, comments, comment.owner
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    logname = "awdeorio"
    post = connection.execute(
        "SELECT owner, filename AS img_url, created AS timestamp "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug, )
    )
    postArray = post.fetchall()

    getOwnerImg = connection.execute(
        "SELECT filename AS owner_img_url "
        "FROM users "
        "WHERE username = ?",
        (postArray[0]["owner"], )
    )
    tempDir = getOwnerImg.fetchall()
    postArray[0]["owner_img_url"] = tempDir[0]["owner_img_url"]

    getComment = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY commentid",
            (postid_url_slug, )
        )
    getComment = getComment.fetchall()

    postArray[0]["comments"] = getComment
    postArray[0]["timestamp"] = \
        arrow.get(postArray[0]["timestamp"]).humanize(arrow.utcnow())

    checkLikes = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE postid = ? AND owner = ? ",
            (postid_url_slug, logname, )
        )
    if len(checkLikes.fetchall()) == 0:
        postArray[0]["userHasLiked"] = False
    else:
        postArray[0]["userHasLiked"] = True

    countLikes = connection.execute(
        "SELECT COUNT(*) as numLikes "
        "FROM likes "
        "WHERE postid = ?",
        (postid_url_slug, )
    )
    tempDir = countLikes.fetchall()
    postArray[0]["numLikes"] = tempDir[0]["numLikes"]

    # Add database info to context
    context = {"logname": logname, "owner": postArray[0]["owner"], \
        "owner_img_url": postArray[0]["owner_img_url"], \
        "postid": postid_url_slug, \
        "img_url": postArray[0]["img_url"], \
        "timestamp": postArray[0]["timestamp"], \
        "comments": postArray[0]["comments"], \
        "likes": postArray[0]["numLikes"], \
        "userHasLiked": postArray[0]["userHasLiked"]   }
    return flask.render_template("post.html", **context)