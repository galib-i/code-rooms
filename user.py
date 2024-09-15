from werkzeug.security import check_password_hash


class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated():
        return True

    def get_id(self):
        return self.username

    def check_password(self, password):
        return check_password_hash(pwash=self.password, password=password)
