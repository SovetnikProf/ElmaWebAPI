#!/usr/bin/python3

import requests as req
import jsonpickle as json
from datetime import datetime, timedelta

app_token = '132D5D0E49B0D30528CB4FEF5FA1FED73FC0DB202C0C1102EE0778B13446A2D89F213BB8BB09BEF22DD09635CBEAF6805E1CEEBD3BA10D844FE635AECE90CA8B'
username = 'ia.chechetkin'
password = '123'
host = 'http://88.87.81.251:1313/API/REST/'

urls = {'auth': 'Authorization/LoginWith',

        'task_create': 'Tasks/Create',
        'task_close': 'Tasks/Close',
        'task_complete': 'Tasks/Complete',
        'task_read': 'Tasks/MarkRead',
        'add_comment': 'Tasks/AddComment',

        'entity_load': 'Entity/Load',
        'entity_query': 'Entity/Query',
        'entity_insert': 'Entity/Insert',
        'entity_update': 'Entity/Update',

        'file_upload': 'Files/Upload',
        'file_download': 'Files/Download',
        'file_size': 'Files/FileSize'
       }

def url(key, value=None):
    return host + urls[key] + ('/{}'.format(value) if value else '')

ses = req.Session()

# ----- auth -----

headers = {'ApplicationToken': app_token,
           'Content-Type': 'application/json; charset=utf-8'}

r = ses.post(url('auth'),
             params={'username': username},
             headers=headers,
             data=password)
r = r.json()

auth_token = r['AuthToken']
session_token = r['SessionToken']
current_user = r['CurrentUserId']

headers = {'ApplicationToken': app_token,
           'AuthToken': auth_token,
           'Content-Type': 'application/json; charset=utf-8'}

# ----- some definitions -----

class Item:
    def __init__(self, name, value=None, data=None, dataarray=None):
        self.Name = name
        self.value = value
        if data is not None:
            self.data = data
        if dataarray is not None:
            self.dataarray = dataarray

    @property
    def value(self):
        return self.Value
    @value.setter
    def value(self, val):
        self.Value = val

    @property
    def data(self):
        return self.Data
    @data.setter
    def data(self, val):
        if type(val) != Data: raise Exception('Type of data must be Data, not {}'.format(type(val)))
        self.Data = val

    @property
    def dataarray(self):
        return self.DataArray
    @dataarray.setter
    def dataarray(self, val):
        if type(val) != DataArray: raise Exception('Type of dataarray must be DataArray, not {}'.format(type(val)))
        self.DataArray = val

    def __str__(self):
        return str(self.__dict__)

class Data:
    def __init__(self, *args):
        self.Items = []
        for item in args:
            self.Items.append(item)

    def add_items(self, *args):
        for item in args:
            self.Items.append(item)

    def __str__(self):
        return str(self.__dict__)

class DataArray(list):
    def add_datas(self, *args):
        for data in args:
            self.append(data)

    def __init__(self, *args):
        for data in args:
            self.append(data)

def get_dict(json_):
    results = []
    if type(json_) != list: json_ = [json_]
    for el in json_:
        results.append({})
        for i in el['Items']:
            results[-1][i['Name']] = i
            results[-1][i['Name']].pop('Name', None)
    return results

def get_json(d):
    return json.encode(d, unpicklable=False)

def date(day=None, month=None, year=None, hour=None, minute=None, now=False):
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
            hour = 12
        if not minute:
            minute = 0
        return datetime(day=day, month=month, year=year, hour=hour, minute=minute).strftime('%Y-%m-%d %H:%M:%S')

# ~~ Working Functions ~~ #

# ----- files -----

def file_upload(file_):
    headers_ = headers
    headers_['FileName'] = file_.split('/')[-1]
    headers_['Content-Type'] = 'application/json'

    with open(file_, 'rb') as f:
        #data = f.read().encode('utf-8')
        r = ses.post(url('file_upload'),
                    headers=headers_,
                    data=f)

    id = r.text[1:-1]
    print('>> File uploaded: ' + id)
    return id

def file_size(id):
    r = ses.get(url('file_size'),
                params={'uid': str(id)},
                headers=headers)
    print('>> File size: ' + r.text)
    return r

def file_download(id):
    size = file_size(id)
    r = ses.get(url('file_download'),
                 params={'uid': str(id)},
                 headers=headers,
                 stream=True)
    local = r.headers.get('Content-Disposition')
    local = list(filter(lambda x: x.find('filename') > -1, local.split(';')))[0].split('=')[-1]
    with open(local, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print('>> File downloaded to ' + local)
    return local

# ----- entities -----

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

    r = ses.post(url('entity_insert', typeid),
                headers=headers,
                data=jsn)
    print('<< Request: ' + jsn)
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

    r = ses.post(url('task_create'),
               headers=headers,
               data=jsn)
    print('<< Request: ' + jsn)
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

    r = ses.post(url('task_close'),
                 headers=headers,
                 data=jsn)
    print('<< Request: ' + jsn)
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

    r = ses.post(url('task_complete'),
                 headers=headers,
                 data=jsn)
    print('<< Request: ' + jsn)
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

    r = ses.post(url('add_comment'),
                 headers=headers,
                 data=jsn)
    print('<< Request: ' + jsn)
    print('>> Response: ' + r.text)
    return r

def mark_read(id):
    d = Data()

    task = Item('TaskId', str(id))
    d.add_items(task)

    jsn = get_json(d)

    r = ses.post(url('task_read'),
                 headers=headers,
                 data=jsn)
    print('<< Request: ' + jsn)
    print('>> Response: ' + r.text)
    return r
