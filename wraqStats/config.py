"""wraqStats development configuration."""
import pathlib
# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'
# Secret key for encrypting cookies
SECRET_KEY = b'\xb3%B\xc9\x19\x1d\xda\xb8S\xa4\xe1,\x01U\xffE\x04AjU\x82\x87\xb7\x1d'
SESSION_COOKIE_NAME = 'login'
# File Upload to var/uploads/
WRAQSTATS_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = WRAQSTATS_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
# Database file is var/insta485.sqlite3
DATABASE_FILENAME = WRAQSTATS_ROOT/'var'/'wraqStats.sqlite3'