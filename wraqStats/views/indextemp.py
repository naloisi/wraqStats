"""
wraqStats index (main) view.
URLs include:
/
"""
import flask
import wraqStats
@wraqStats.app.route('/testhello')
def show_hello():
    """Display /testhello route."""

    # Connect to database
    connection = wraqStats.model.get_db()
    # Query database
    logname = "awdeorio"
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username != ?",
        (logname, )
    )
    users = cur.fetchall()

    # Add database info to context
    context = {"users": users}
    return flask.render_template("indextemp.html", **context)