# -*- coding: utf-8 -*-
from sys import version_info
if version_info.major > 2:
    from urllib.parse import quote_plus, unquote_plus
else:
    from __future__ import unicode_literals
    from urllib import quote_plus, unquote_plus

import requests as req
from jsonpickle import encode as json_encode
from re import search as re_search
from copy import copy
from datetime import datetime


# для тестов: токен класса вложений
ATTACHMENT_TOKEN = 'd4553858-96c6-4ed5-87dd-7a0429bf5cf3'
#             токен тестового бизнес-процесса
PROCESS_TOKEN = '381769ca-715b-4bf5-9806-6d43423f67f3'
#             токен класса контрагентов
CONTRACTOR_TOKEN = '73bf0874-4f9d-4e5a-a1f9-0b44c9a5aa88'
#             токен класса группы пользователей
USERGROUP_TOKEN = 'cf104645-72b9-4ef6-866c-8add9312fd9d'


CONTENT_TYPE_JSON = 'application/json'


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

def url(host, key, value=None):
    """ Возвращает полный текст url, взяв значения по ключу key из словаря urls.
        Опциональный аргумент value используется для добавления после
        основного url.
    """
    return host + urls[key] + ('/{}'.format(value) if value else '')

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
        self.Name = str(name)
        self.Value = str(value)
        if data is not None:
            self.Data = data
        if dataarray is not None:
            self.DataArray = dataarray

    def __repr__(self):
        return get_json(self)

class Data:
    """ Web-API Item List -- вспомогательный объект для описания Item.Data.

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

    def __unicode__(self):
        return get_json(self)

class DataArray(list):
    """ Web-API Data List -- вспомогательный объект для описания Item.DataArray,
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

    def __unicode__(self):
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

class ELMA(object):
    def __init__(self, host, app_token, username='', password='', silent=False):
        self.host = host
        self.app_token = app_token
        self.username = username
        self.password = password
        self.silent = silent

        # создаем сессию, в которой будем работать, записываем её в переменную session
        # в дальнейшем все запросы идут через сессию session
        self.session = req.Session()

        # объявляем переменные для запросов
        # заголовки запросов
        self.headers = {'ApplicationToken': app_token,
                        'Content-Type': 'application/json; charset=utf-8'}

        # токен авторизации, изменять значение этой переменной после логина
        self.auth_token = None
        # токен сессии, изменять значение этой переменной после логина
        self.session_token = None
        # ID текущего пользователя, изменять значение этой переменной после логина
        self.current_user = None

    # ~~~~~~ Обертка функций API ~~~~~~ #


    # ----- Авторизация (IAuthorizationService) -----

    def login(self, username='', password=''):
        """ Авторизация по имени пользователя и паролю.
        Две возможности задания параметров: либо при вызове функции,
        либо при создании экземпляра класса.

        Параметры:
            username [str] : логин пользователя

            password [str] : пароль пользователя

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        usr, pwd = '', ''
        if username:
            usr = username
        elif self.username:
            usr = self.username
        else:
            raise Exception('Elma[login]: No username given')
        if password:
            pwd = password
        elif self.password:
            pwd = self.password
        else:
            raise Exception('Elma[login]: No password given')

        r = self.session.post(url(self.host, 'auth_login'),
                              params={'username': usr},
                              headers=self.headers,
                              data=pwd)

        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> Response: ' + r.text)
        return r

    def auto_login(self, username='', password=''):
        """ Функция для автоматического логина. Перезаписывает значения нужных
            переменных.
        """
        usr, pwd = '', ''
        if username:
            usr = username
        elif self.username:
            usr = self.username
        else:
            raise Exception('Elma[auto_login]: No username given')
        if password:
            pwd = password
        elif self.password:
            pwd = self.password
        else:
            raise Exception('Elma[auto_login]: No password given')

        # логинимся за пользователя
        r = self.login(usr, pwd)
        if not self.silent:
            print(r.text)

        # вытаскиваем нужные параметры, прописываем в заголовок токен авторизации
        try:
            self.auth_token = r.json()['AuthToken']
            self.session_token = r.json()['SessionToken']
            self.current_user = r.json()['CurrentUserId']
            self.headers['AuthToken'] = self.auth_token
        # если не залогинились -- выводим ошибку
        except KeyError:
            raise Exception('Elma[auto_login]: Failed to log in')
        return r

    def server_time(self):
        """ Функция получения серверного времени. Поскольку для этого требуется
            авторизация, то можно через промежуток времени запускать эту функцию для
            получения текущего состояния авторизации, а при получении 401 ошибки
            получать новый токен авторизации.

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        r = self.session.get(url(self.host, 'auth_time'),
                             headers=self.headers)

        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> Server time: ' + r.text)
        return r

    # ----- Файлы (IFilesService) -----

    def file_upload(self, file_):
        """ Функция загрузки файла на сервер. Данный сервис заливает файл не как
            объект "File", а как объект вложения "Attachment".

        Обязательные параметры:
            file_ [str] : путь к файлу

        Возвращает:
            [str] : Uid загруженного файла
        """
        headers = self.headers
        headers['FileName'] = quote_plus(file_.split('/')[-1])
        headers['Content-Type'] = CONTENT_TYPE_JSON

        # файл должен передаваться в потоке, поэтому используем оператор with
        # открываем файл в байтовом режиме 'b'
        with open(file_, 'rb') as f:
            r = self.session.post(url(self.host, 'file_upload'),
                                  headers=headers,
                                  data=f)

        id = r.text[1:-1]

        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> File uploaded: ' + id)
        return id

    def file_size(self, id):
        """ Функция, определяющая размер файла на сервере по его Uid.

        Обязательные параметры:
            id [str] : Uid файла, размер которого нужно узнать

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        r = self.session.get(url(self.host, 'file_size'),
                             params={'uid': str(id)},
                             headers=self.headers)

        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> File size: ' + r.text)
        return r

    def file_download(self, id, content=False, link=False):
        """ Функция, скачивающая файл с сервера по его Uid.

        Обязательные параметры:
            id [str] : Uid файла, размер которого нужно узнать

        Необязательные параметры:
            content [bool] : если True, то функция не будет скачивать файл,
                             а вернет поток для его сторонней обработки
            link [bool] : если True, то функция не будет скачивать файл,
                          а вернет URL файла для внешнего скачивания

        Возвращает:
            [str] : локальное имя файла
        """
        if link:
            return url(self.host, 'file_download') + '?uid=' + str(id)

        r = self.session.get(url(self.host, 'file_download'),
                             params={'uid': str(id)},
                             headers=self.headers,
                             stream=True)
        if not self.silent:
            print('<< Request: ' + r.url)

        if content:
            return r.content

        # получаем имя файла из заголовка 'Content-Disposition'
        local = r.headers.get('Content-Disposition')
        if not self.silent:
            print(local)
        try:
            # внутри, помимо имени файла, имеется другая информация, поэтому
            # вырезаем часть с нужной информацией
            local = re_search(r'filename=(?P<fname>.*)?;', local).group('fname')
        except:
            try:
                local = re_search(r'filename.*?\'\'(?P<fname>.*)', local).group('fname')
                local = unquote_plus(local)
            except:
                local = 'downloaded'
        with open(local, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                # чанк за чанком пишем в файл
                if chunk:
                    f.write(chunk)

        if not self.silent:
            print('>> File downloaded to ' + local)
        return local

    # ----- Объекты (IEntityService) -----

    def load_entity(self, typeid, entid):
        """ Функция, получающая объект определенного типа с определенным ID.

        Обязательные параметры:
            typeid [str] : тип объекта

            entid [str] : ID объекта

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        r = self.session.get(url(self.host, 'entity_load'),
                             params={'type': str(typeid), 'id': str(entid)},
                             headers=self.headers)
        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> Response: ' + r.text)
        return r

    def query_entity(self, typeid, query=None, filter_=None, limit=None, offset=None, sort=None, filteruid=None, filterdata=None):
        """ Функция, получающая выборку объектов определенного типа.

        Обязательные параметры:
            typeid [str] : тип объекта

        Необязательные параметры:
            query [str] : ???

            filter_ [str] : ???

            limit [str] : ???

            offset [str] : ???

            sort [str] : ???

            filteruid [str] : ???

            filterdata [str] : ???

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
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

        r = self.session.get(url(self.host, 'entity_query'),
                             params=params,
                             headers=self.headers)
        if not self.silent:
            print('<< Request: ' + r.url)
            print('>> Response: ' + r.text)
        return r

    def insert_entity(self, typeid, name, responsible):
        """ Функция, создающая объект определенного типа.

        Обязательные параметры:
            typeid [str] : тип объекта

            name [str] : имя объекта

            responsible [str] : id ответственного пользователя *

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера

        * Функция тестировалась на создании контрагентов -- имя и ответственный
          являются двумя обязательными параметрами при их создании.
        """
        d = Data()

        name = Item('Name', name)
        resp = Item('Responsible')
        resp.Data = Data(Item('Id', responsible))

        d.add_items(name, resp)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'entity_insert', typeid),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    # ----- Задачи (Tasks) -----

    def create_task(self, subject, executors, start_date, end_date, description=None, files=None, controler=None, upload=True):
        """ Функция, создающая задачу.

        Обязательные параметры:
            subject [str] : тема задачи

            executors [str / list(str)] : id / список id пользователей, являющихся
                                          исполнителями задачи

            start_date [str] : дата начала задачи

            end_date [str] : дата окончания задачи

        Необязательные параметры:
            description [str] : описание задачи

            files [str / list(str)] : наименование / список наименований   ИЛИ
                                      Uid / список Uid файлов, приложенных к задаче

            controler [str] : id пользователя, являющегося контролером исполнения

            upload [bool] : если False, то переменная files будет рассматриваться
                            как Uid / список Uid файлов (для прикрепления уже
                            залитых файлов)
        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        # создаем тело запроса
        d = Data()

        # обязательные параметры
        subj = Item('Subject', subject)

        excr = Item('Executor', data=Data())
        # если исполнитель один, обернуть в список для использования в цикле
        if type(executors) != list: executors = [executors]
        for ex in executors:
            excr.Data.add_items(Item('Id', ex))

        strdate = Item('StartDate', start_date)
        enddate = Item('EndDate', end_date)

        # добавляем обязательные параметры в запрос
        d.add_items(subj, excr, strdate, enddate)

        # опциональные параметры
        if description:
            desc = Item('Description', description)
            d.add_items(desc)

        if files:
            attach = Item('Attachments', dataarray=DataArray())
            if type(files) != list: files = [files]
            for f in files:
                # в задачах при прикреплении файлов Data должна быть обёрнута в
                # дополнительный Item('File'), который обёрнут в еще одну Data
                attach.DataArray.add_datas(Data(Item('File', data=Data(Item('Uid',
                                           self.file_upload(f) if upload else f)))))
            d.add_items(attach)

        if controler:
            cont = Item('ControlUser', data=Data())
            if type(controler) != list: controler = [controler]
            for con in controler:
                cont.Data.add_items(Item('Id', con))
            d.add_items(cont)

        # запрос сформирован, преобразуем его в json
        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        # посылаем запрос на сервер, ждем ответа
        r = self.session.post(url(self.host, 'task_create'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        # возвращаем ответ сервера
        return r

    def close_task(self, id, text=None, files=None, upload=True):
        """ Функция, закрывающая задачу.

        Обязательные параметры:
            id [str] : id задачи

        Необязательные параметры:
            text [str] : текст комментария

            files [str / list(str)] : наименование / список наименований   ИЛИ
                                      Uid / список Uid файлов, приложенных к комментарию

            upload [bool] : если False, то переменная files будет рассматриваться
                            как Uid / список Uid файлов (для прикрепления уже
                            залитых файлов)
        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        task = Item('TaskId', id)
        d.add_items(task)

        # если передан текст или файлы, то необходимо добавить в запрос комментарий
        if text or files:
            # если переданы только файлы, то текст комментария оставляем пустым
            if not text: text = ''
            com = Item('Comment')
            com.Data = Data(Item('Text', text))

            if files:
                attach = Item('Attachments', dataarray=DataArray())
                if type(files) != list: files = [files]
                for f in files:
                    # в отличие от задачи, для прикрепления файлов к комментарию их
                    # не нужно дополнительно оборачивать
                    attach.DataArray.add_datas(Data(Item('Uid',
                                               self.file_upload(f) if upload else f)))
                com.Data.add_items(attach)

            d.add_items(com)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'task_close'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    def complete_task(self, id, text=None, files=None, upload=True):
        """ Функция, выполняющая задачу.

        Обязательные параметры:
            id [str] : id задачи

        Необязательные параметры:
            text [str] : текст комментария

            files [str / list(str)] : наименование / список наименований   ИЛИ
                                      Uid / список Uid файлов, приложенных к комментарию

            upload [bool] : если False, то переменная files будет рассматриваться
                            как Uid / список Uid файлов (для прикрепления уже
                            залитых файлов)
        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        task = Item('TaskId', id)
        d.add_items(task)

        if text or files:
            if not text: text = ''
            com = Item('Comment')
            com.Data = Data(Item('Text', text))

            if files:
                attach = Item('Attachments', dataarray=DataArray())
                if type(files) != list: files = [files]
                for f in files:
                    attach.DataArray.add_datas(Data(Item('Uid',
                                               self.file_upload(f) if upload else f)))
                com.Data.add_items(attach)

            d.add_items(com)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'task_complete'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    def add_comment(self, id, text, files=None, upload=True):
        """ Функция, добавляющая комментарий к определенной задаче.

        Обязательные параметры:
            id [str] : id задачи

            text [str] : текст комментария

        Необязательные параметры:
            files [str / list(str)] : наименование / список наименований   ИЛИ
                                      Uid / список Uid файлов, приложенных к комментарию

            upload [bool] : если False, то переменная files будет рассматриваться
                            как Uid / список Uid файлов (для прикрепления уже
                            залитых файлов)
        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        task = Item('TaskId', id)
        d.add_items(task)

        com = Item('Comment')
        com.Data = Data(Item('Text', text))

        if files:
            attach = Item('Attachments', dataarray=DataArray())
            if type(files) != list: files = [files]
            for f in files:
                attach.DataArray.add_datas(Data(Item('Uid',
                                           self.file_upload(f) if upload else f)))
            com.Data.add_items(attach)

        d.add_items(com)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'comment_add'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    def mark_read(self, id):
        """ Функция, помечающая задачу как прочитанную.

        Обязательные параметры:
            id [str] : id задачи

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        task = Item('TaskId', id)
        d.add_items(task)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'task_read'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    # ----- Процессы (Workflow) -----

    def make_context(self, **kwargs):
        """ Вспомогательная функция, выстраивающая Data по словарю аргументов.

        Например,
            make_context(key1='value1', key2=Data(Item('name', 'value')))
        создаст объект Data, преобразующийся в следующий json:
            {"Items": [{"Name": "key1", "Value": "value1"},
                       {"Data": {"Items": [{"Name": "name", "Value": "value"}]},
                        "Name": "key2", "Value": "None"}
                      ]}

        Возвращает:
            [Data] : созданный объект данных
        """
        c = Data()
        for key in kwargs:
            i = Item(key)
            if type(kwargs[key]) == Data:
                i.Data = kwargs[key]
            elif type(kwargs[key]) == DataArray:
                i.DataArray = kwargs[key]
            else:
                i.value = kwargs[key]
            c.add_items(i)
        return c

    def start_process(self, name, context, process_token, process_header=None):
        """ Функция, запускающая бизнес-процесс.

        Обязательные параметры:
            name [str] : имя экземпляра процесса

            context [Data] : переменные контекста процесса

            process_token [str] : токен процесса

        Необязательные параметры:
            process_header [str] : ???

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        proc = Item('ProcessName', name)
        cont = Item('Context', data=context)
        ptok = Item('ProcessToken', process_token)
        d.add_items(proc, cont, ptok)

        if process_header:
            phid = Item('ProcessHeaderId', process_header)
            d.add_items(phid)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'process_start'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

    def process_status(self, token):
        """ Функция, проверяющая статус исполнения бизнес-процесса.

        Обязательные параметры:
            token [str] : токен экземпляра бизнес-процесса

        Возвращает:
            [requests.models.Response] : объект, хранящий ответ сервера
        """
        d = Data()

        etok = Item('ExecutionToken', token)
        d.add_items(etok)

        jsn = get_json(d)

        if not self.silent:
            print('<< Request: ' + jsn)
        r = self.session.post(url(self.host, 'process_status'),
                              headers=self.headers,
                              data=jsn)
        if not self.silent:
            print('>> Response: ' + r.text)
        return r

if __name__ == '__main__':
    elma = ELMA('http://88.87.81.251:1313/API/REST/',
                '132D5D0E49B0D30528CB4FEF5FA1FED73FC0DB202C0C1102EE0778B13446A2D89F213BB8BB09BEF22DD09635CBEAF6805E1CEEBD3BA10D844FE635AECE90CA8B',
                username='Oparler',
                password='"^73jhg4hgJHGf3@\'"',
                silent=False)
