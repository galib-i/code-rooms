from werkzeug.security import check_password_hash


class User:
    """Holds the current user data"""
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated():
        """Checks if the user is logged in"""
        return True

    def get_id(self):
        """Returns the username - overrides method for Flask-Login"""
        return self.username

    def check_password(self, password):
        """Checks if the entered password matches the stored one

        Args:
            password (str): plaintext password

        Returns:
            bool: True if the password matches, False otherwise
        """
        return check_password_hash(pwhash=self.password, password=password)
