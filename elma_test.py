#!/usr/bin/python3

import requests as req
from jsonpickle import encode as json_encode
from re import search as re_search
from copy import copy
from datetime import datetime
from urllib.parse import quote_plus # from urllib import quote_plus в python2

# токен приложения
app_token = '132D5D0E49B0D30528CB4FEF5FA1FED73FC0DB202C0C1102EE0778B13446A2D89F213BB8BB09BEF22DD09635CBEAF6805E1CEEBD3BA10D844FE635AECE90CA8B'
# логин пользователя
username = 'ia.chechetkin'
# пароль пользователя
password = '123'
# хост, на котором размещается Elma (обязательно должен начинаться с протокола)
host = 'http://88.87.81.251:1313/API/REST/'

# для тестов: токен класса вложений
ATTACHMENT_TOKEN = 'd4553858-96c6-4ed5-87dd-7a0429bf5cf3'
# для тестов: токен тестового бизнес-процесса
PROCESS_TOKEN = '381769ca-715b-4bf5-9806-6d43423f67f3'


# ~~~~~~ некоторые определения ~~~~~~ #


# словарь url для сокращения запросов в коде
urls = {'auth_login': 'Authorization/LoginWith',
        'auth_time': 'Authorization/ServerTime',

        'task_create': 'Tasks/Create',
        'task_close': 'Tasks/Close',
        'task_complete': 'Tasks/Complete',
        'task_read': 'Tasks/MarkRead',
        'comment_add': 'Tasks/AddComment',

        'entity_load': 'Entity/Load',
        'entity_query': 'Entity/Query',
        'entity_insert': 'Entity/Insert',
        'entity_update': 'Entity/Update',

        'file_upload': 'Files/Upload',
        'file_download': 'Files/Download',
        'file_size': 'Files/FileSize',

        'process_start': 'Workflow/StartProcessAsync',
        'process_status': 'Workflow/ExecuteUserTaskStatus'
       }

def url(key, value=None):
    """ Возвращает полный url, взяв значения по ключу key из словаря urls.
        Опциональный аргумент value используется для добавления после
        основного url.
    """
    return host + urls[key] + ('/{}'.format(value) if value else '')

# создаем сессию, в которой будем работать
ses = req.Session()

# переменные для запросов
# заголовки запросов
headers = {'ApplicationToken': app_token,
           'Content-Type': 'application/json; charset=utf-8'}
# токен авторизации, изменять значение этой переменной после логина
auth_token = None
# токен сессии, изменять значение этой переменной после логина
session_token = None
# ID текущего пользователя, изменять значение этой переменной после логина
current_user = None

class Item:
    """ Web-API Data Item -- основной объект для использования в теле запроса.

    Представление в json:
        Item = {'Name': str, 'Value': str, 'Data': Data, 'DataArray': DataArray}

    Обязательные параметры:
        name [str] : Название объекта

    Необязательные параметры (как правило в объекте используется один из трёх):
        value [str] : Значение в объекте

        data [Web-API Item List] : Передаваемые данные в объекте

        dataarray [Web-API Data List] : Список передаваемых данных в объекте
                                        (в справке помечается как "[i]")
    """
    def __init__(self, name, value=None, data=None, dataarray=None):
        self.name = name
        self.value = value
        if data is not None:
            self.data = data
        if dataarray is not None:
            self.dataarray = dataarray

    @property
    def name(self):
        return self.Name
    @name.setter
    def name(self, val):
        self.Name = str(val)

    @property
    def value(self):
        return self.Value
    @value.setter
    def value(self, val):
        self.Value = str(val)

    @property
    def data(self):
        return self.Data
    @data.setter
    def data(self, val):
        if type(val) != Data:
            raise Exception('Type of data must be Data, not {}'.format(type(val)))
        self.Data = val

    @property
    def dataarray(self):
        return self.DataArray
    @dataarray.setter
    def dataarray(self, val):
        if type(val) != DataArray:
            raise Exception('Type of dataarray must be DataArray, not {}'.format(type(val)))
        self.DataArray = val

    def __str__(self):
        return get_json(self)

class Data:
    """ Web-API Item List -- вспомогательный объект для описания Item.data.

    Представление в json:
        Data = {'Items': [Item, Item, ...]}

    Встроенные методы:
        add_items(*args) : добавляет элементы args в коллекцию Items
    """
    def __init__(self, *args):
        self.Items = []
        for item in args:
            self.Items.append(item)

    def add_items(self, *args):
        for item in args:
            self.Items.append(item)

    def __str__(self):
        return get_json(self)

class DataArray(list):
    """ Web-API Data List -- вспомогательный объект для описания Item.dataarray,
        отнаследован от списка для корректного представления в json.

    Представление в json:
        DataArray = [Data, Data, ...]

    Встроенные методы:
        add_datas(*args) : добавляет элементы args в список.
    """
    def add_datas(self, *args):
        for data in args:
            self.append(data)

    def __init__(self, *args):
        for data in args:
            self.append(data)

    def __str__(self):
        return get_json(self)

def get_dict(json_):
    """ Возвращает список словарей, построенных на вовращаемом Elm-ой json-е.
        Поскольку возвращаемый json по сути представляет собой json
        элемента Data * (или DataArray), то для более удобного поиска значений
        используется эта функция.

        Например, следующий список
            [{"Items": [{"Name": "Uid", "Value": "token", "Data": {}, "DataArray": []}]}]
        будет преобразован в
            [{'Uid': {'Value': 'token', 'DataArray': [], 'Data': {}}}]}]
        и значение свойства Uid можно получить через ключ
            s[0]['Uid'] = {'Value': 'token', 'Data': {}, 'DataArray': []}

        * Здесь речь о Item, Data и DataArray идет не как о классах, а как о
          структурах данных (их json-представлениях), используемых Elm-ой.
    """
    results = []
    # поскольку функция одна и для получаемого json DataArray, и для json Data,
    # то проверяем тип входного параметра -- на входе должен быть список.
    if type(json_) != list: json_ = [json_]
    for el in json_:
        # для каждого элемента Data в DataArray создаем словарь
        results.append({})
        for i in el['Items']:
            # для каждого Item внутри Data создаем позицию в словаре, ключ
            # которой -- значение свойства 'Name', а значение -- элемент Item
            # за исключением свойства 'Name' (дабы избежать дублирования данных)
            results[-1][i['Name']] = copy(i)
            results[-1][i['Name']].pop('Name', None)
    return results

def get_json(d):
    """ Псевдоним для функции jsonpickle.encode. """
    return json_encode(d, unpicklable=False)

def date(day=None, month=None, year=None, hour=None, minute=None, now=False):
    """ Псевдоним для datetime().strtime. Возвращает строковое представление даты.

    Необязательные параметры:
        day [int] (1 <= day <= 31) : день месяца (стандартное значение -- сегодня)

        month [int] (1 <= month <= 12) : месяц (стандартное значение -- текущий месяц)

        year [int] (0 < year) : год (стандартное значение -- текущий год)

        hour [int] (0 <= hour <= 23) : час  (стандартное значение -- 8 утра)

        minute [int] (0 <= minute <= 59) : минута (стандартное значение -- 0)

        now [bool] : если True, будет использовано текущее время
    """
    if now:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        if not day:
            day = datetime.now().day
        if not month:
            month = datetime.now().month
        if not year:
            year = datetime.now().year
        if not hour:
            hour = 8
        if not minute:
            minute = 0
        return datetime(day=day, month=month, year=year, hour=hour, minute=minute).strftime('%Y-%m-%d %H:%M:%S')


# ~~~~~~ Обертка функций API ~~~~~~ #


# ----- Авторизация (IAuthorizationService) -----

def login(username, password):
    """ Авторизация по логину и паролю.

    Обязательные параметры:
        username [str] : логин пользователя

        password [str] : пароль пользователя

    Возвращает:
        [requests.models.Response] : объект, хранящий ответ сервера
    """
    r = ses.post(url('auth_login'),
                 params={'username': username},
                 headers=headers,
                 data=password)
    print('<< Request: ' + r.url)
    print('>> Response: ' + r.text)
    return r

def server_time():
    """ Функция получения серверного времени. Поскольку для этого требуется
        авторизация, то можно через промежуток времени запускать эту функцию для
        получения текущего состояния авторизации, а при получении 401 ошибки
        получать новый токен авторизации.

    Возвращает:
        [requests.models.Response] : объект, хранящий ответ сервера
    """
    r = ses.get(url('auth_time'),
                headers=headers)
    print('<< Request: ' + r.url)
    print('>> Server time: ' + r.text)
    return r

# ----- Файлы (IFilesService) -----

def file_upload(file_):
    """ Функция загрузки файла на сервер. Данный сервис заливает файл не как
        объект "File", а как объект вложения "Attachment".
    
    Обязательные параметры:
        file_ [str] : путь к файлу

    Возвращает:
        [str] : Uid загруженного файла
    """
    headers_ = headers
    headers_['FileName'] = quote_plus(file_.split('/')[-1])
    headers_['Content-Type'] = 'application/json'

    # файл должен передаваться в потоке, поэтому используем оператор with
    # открываем файл в байтовом режиме 'b'
    with open(file_, 'rb') as f:
        r = ses.post(url('file_upload'),
                    headers=headers_,
                    data=f)

    id = r.text[1:-1]

    print('<< Request: ' + r.url)
    print('>> File uploaded: ' + id)
    return id

def file_size(id):
    """ Функция, определяющая размер файла на сервере по его Uid.

    Обязательные параметры:
        id [str] : Uid файла, размер которого нужно узнать

    Возвращает:
        [requests.models.Response] : объект, хранящий ответ сервера
    """
    r = ses.get(url('file_size'),
                params={'uid': str(id)},
                headers=headers)
    print('<< Request: ' + r.url)
    print('>> File size: ' + r.text)
    return r

def file_download(id):
    """ Функция, скачивающая файл с сервера по его Uid.

    Обязательные параметры:
        id [str] : Uid файла, размер которого нужно узнать

    Возвращает:
        [str] : локальное имя файла
    """
    r = ses.get(url('file_download'),
                 params={'uid': str(id)},
                 headers=headers,
                 stream=True)
    print('<< Request: ' + r.url)

    # получаем имя файла из заголовка 'Content-Disposition'
    local = r.headers.get('Content-Disposition')
    try:
        # внутри, помимо имени файла, имеется другая информация, поэтому
        # вырезаем часть с нужной информацией
        local = re_search(r'filename=(?P<fname>.*)?;', local).group('fname')
    except:
        local = 'downloaded'
    with open(local, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            # чанк за чанком пишем в файл
            if chunk:
                f.write(chunk)

    print('>> File downloaded to ' + local)
    return local

# ----- Объекты (IEntityService) -----

def load_entity(typeid, entid):
    r = ses.get(url('entity_load'),
                params={'type': str(typeid), 'id': str(entid)},
                headers=headers)
    print('<< Request: ' + r.url)
    print('>> Response: ' + r.text)
    return r

def query_entity(typeid, query=None, filter_=None, limit=None, offset=None, sort=None, filteruid=None, filterdata=None):
    params = {'type': str(typeid)}
    if query:
        params['q'] = str(query)
    if limit:
        params['limit'] = str(limit)
    if offset:
        params['offset'] = str(offset)
    if sort:
        params['sort'] = str(sort)
    if filteruid:
        params['filterProviderUid'] = str(filteruid)
    if filterdata:
        params['filterProviderData'] = str(filterdata)
    if filter_:
        params['filter'] = str(filter_)

    r = ses.get(url('entity_query'),
                params=params,
                headers=headers)
    print('<< Request: ' + r.url)
    print('>> Response: ' + r.text)
    return r

def insert_entity(typeid, name, responsible):
    d = Data()

    name = Item('Name', str(name))
    resp = Item('Responsible')
    resp.data = Data(Item('Id', str(responsible)))

    d.add_items(name, resp)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('entity_insert', typeid),
                headers=headers,
                data=jsn)
    print('>> Response: ' + r.text)
    return r

# ----- tasks -----

# there aren't many existed arguments in command line -- look at http://88.87.81.251:1313/API/Help/Type?uid=298b2c71-619f-463c-95b2-8e029085680d
def create_task(subject, executors, start_date, end_date, description=None, files=None, controler=None, upload=True):
    d = Data()

    # required arguments
    subj = Item('Subject', str(subject))
    excr = Item('Executor', data=Data())
    if type(executors) != list: executors = [executors]
    for ex in executors:
        excr.data.add_items(Item('Id', str(ex)))
    strdate = Item('StartDate', str(start_date))
    enddate = Item('EndDate', str(end_date))

    d.add_items(subj, excr, strdate, enddate)

    # optional arguments
    if description:
        desc = Item('Description', str(description))
        d.add_items(desc)

    if files:
        attach = Item('Attachments', dataarray=DataArray())
        if type(files) != list: files = [files]
        for f in files:
            attach.dataarray.add_datas(Data(Item('File', data=Data(Item('Uid', file_upload(f) if upload else f)))))
        d.add_items(attach)

    if controler:
        cont = Item('ControlUser', data=Data())
        if type(controler) != list: controler = [controler]
        for con in controler:
            cont.data.add_items(Item('Id', str(con)))
        d.add_items(cont)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('task_create'),
               headers=headers,
               data=jsn)
    print('>> Response: ' + r.text)
    return r

def close_task(id, text=None, files=None, upload=True):
    d = Data()

    task = Item('TaskId', str(id))
    d.add_items(task)

    if text or files:
        if not text: text = ''
        com = Item('Comment')
        com.data = Data(Item('Text', str(text)))

        if files:
            attach = Item('Attachments', dataarray=DataArray())
            if type(files) != list: files = [files]
            for f in files:
                attach.dataarray.add_datas(Data(Item('Uid', file_upload(f) if upload else f)))
            com.data.add_items(attach)

        d.add_items(com)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('task_close'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def complete_task(id, text=None, files=None, upload=True):
    d = Data()

    task = Item('TaskId', str(id))
    d.add_items(task)

    if text or files:
        if not text: text = ''
        com = Item('Comment')
        com.data = Data(Item('Text', str(text)))

        if files:
            attach = Item('Attachments', dataarray=DataArray())
            if type(files) != list: files = [files]
            for f in files:
                attach.dataarray.add_datas(Data(Item('Uid', file_upload(f) if upload else f)))
            com.data.add_items(attach)

        d.add_items(com)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('task_complete'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def add_comment(id, text, files=None, upload=True):
    d = Data()

    task = Item('TaskId', str(id))
    d.add_items(task)

    com = Item('Comment')
    com.data = Data(Item('Text', str(text)))

    if files:
        attach = Item('Attachments', dataarray=DataArray())
        if type(files) != list: files = [files]
        for f in files:
            attach.dataarray.add_datas(Data(Item('Uid', file_upload(f) if upload else f)))
        com.data.add_items(attach)

    d.add_items(com)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('comment_add'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def mark_read(id):
    d = Data()

    task = Item('TaskId', str(id))
    d.add_items(task)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('task_read'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

# ----- processes -----

def make_context(**kwargs):
    c = Data()
    for key in kwargs:
        i = Item(key)
        if type(kwargs[key]) == Data:
            i.data = kwargs[key]
        elif type(kwargs[key]) == DataArray:
            i.dataarray = kwargs[key]
        else:
            i.value = kwargs[key]
        c.add_items(i)
    return c

# pass files without File Item
def start_process(name, context, process_token=None, process_header=None):
    d = Data()

    proc = Item('ProcessName', str(name))
    cont = Item('Context', data=context)
    d.add_items(proc, cont)

    if process_token:
        ptok = Item('ProcessToken', str(process_token))
        d.add_items(ptok)
    if process_header:
        phid = Item('ProcessHeaderId', str(process_header))
        d.add_items(phid)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('process_start'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def process_status(token):
    d = Data()

    etok = Item('ExecutionToken', str(token))
    d.add_items(etok)

    jsn = get_json(d)

    print('<< Request: ' + jsn)
    r = ses.post(url('process_status'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

if __name__ == '__main__':
    l = login(username, password)
    l = l.json()

    try:
        auth_token = l['AuthToken']
        session_token = l['SessionToken']
        current_user = l['CurrentUserId']
        headers['AuthToken'] = auth_token
    except KeyError:
        raise Exception('Failed to log in!')
