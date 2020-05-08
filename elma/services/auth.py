def login_with_username(username, password, headers={}):
    import requests
    from elma.settings import CREDENTIALS

    session = requests.Session()
    session.headers = headers
    res = session.post(f'{CREDENTIALS["ELMA"]["host"]}API/REST/Authorization/LoginWith',
                       params={'username': username},
                       data=password)

    try:
        return res.json()
    except requests.RequestException:
        raise ConnectionError(res.text)


def server_time():
    """ Needs authorization """
    pass
