from elma.settings import CREDENTIALS


class Connection:
    auth = ''
    session = ''
    user = 0

    __instance = None

    def __init__(self):
        from elma.services.auth import login_with_username

        if not Connection.__instance:
            headers = {'ApplicationToken': CREDENTIALS['ELMA']['token'],
                       'Content-Type': 'application/json; charset=utf-8'}

            try:
                resp = login_with_username(CREDENTIALS['ELMA']['username'],
                                           CREDENTIALS['ELMA']['password'],
                                           headers=headers)
                self.auth = resp['AuthToken']
                self.session = resp['SessionToken']
                self.user = resp['CurrentUserId']
            except ConnectionError:
                pass  # do smth

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Connection()
        return cls.__instance

    def get_session(self):
        import requests

        session = requests.Session()
        session.headers = {'ApplicationToken': CREDENTIALS['ELMA']['token'],
                           'Content-Type': 'application/json; charset=utf-8',
                           'AuthToken': self.auth,
                           'SessionToken': self.session}

