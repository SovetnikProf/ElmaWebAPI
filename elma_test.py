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
        'entity_load': 'Entity/Load',
        'entity_query': 'Entity/Query',
        'entity_insert': 'Entity/Insert',
        'file_upload': 'Files/Upload',
        'file_download': 'Files/Download',
        'add_comment': 'Tasks/AddComment',
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
    Items = []

    def __init__(self, name=None, value=None, data=None, dataarray=None):
        def todata(items):
            dat = Item()
            dat.Items = [item for item in items]
            return dat

        if dataarray:
            self.DataArray = [todata([dat]) for dat in dataarray]
        if data:
            self.Data = todata(data)
        self.Name = name
        self.Value = value

    def __str__(self):
        return str(self.__dict__)

def get_dict(json_):
    results = []
    for el in json_:
        results.append({})
        for i in el['Items']:
            results[-1][i['Name']] = i
            results[-1][i['Name']].pop('Name', None)
    return results

d = {'Items': []}
def get_json():
    global d
    s = json.encode(d, unpicklable=False)
    d = {'Items': []}
    return s

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
    print('>> Response: ' + r.text)
    return r

def insert_entity(typeid, name, responsible):
    name = Item('Name', str(name))
    resp = Item('Responsible', None, [Item('Id', str(responsible))])

    d['Items'].append(name)
    d['Items'].append(resp)

    jsn = get_json()

    r = ses.post(url('entity_insert', typeid),
                headers=headers,
                data=jsn)
    print('>> Response: ' + r.text)
    return r

# ----- tasks -----

# there aren't many existed arguments in command line -- look at http://88.87.81.251:1313/API/Help/Type?uid=298b2c71-619f-463c-95b2-8e029085680d
def create_task(subject, executors, start, end, description, file_=None, file_id=None):
    subj = Item('Subject', str(subject))
    if type(executors) == type([]):
        excr = Item('Executor', None, [Item('Id', str(ex)) for ex in executors])
    else:
        excr = Item('Executor', None, [Item('Id', str(executors))])
    stdate = Item('StartDate', str(start))
    endate = Item('EndDate', str(end))
    desc = Item('Description', str(description))
    if file_:
        attach = Item('Attachments', None,
                      dataarray=[Item('File', None, [Item('Uid', file_upload(file_))])])
    if file_id:
        attach = Item('Attachments', None,
                      dataarray=[Item('File', None, [Item('Uid', file_id)])])

    d['Items'].append(subj)
    d['Items'].append(excr)
    d['Items'].append(stdate)
    d['Items'].append(endate)
    d['Items'].append(desc)
    d['Items'].append(attach)

    jsn = get_json()

    r = ses.post(url('task_create'),
               headers=headers,
               data=jsn)
    print('>> Response: ' + r.text)
    return r

def close_task(id, comment=''):
    task = Item('TaskId', str(id))
    comm = Item('Comment', None, [Item('Text', str(comment))])

    d['Items'].append(task)
    d['Items'].append(comm)

    jsn = get_json()

    r = ses.post(url('task_close'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def complete_task(id, comment=''):
    task = Item('TaskId', str(id))
    comm = Item('Comment', None, [Item('Text', str(comment))])

    d['Items'].append(task)
    d['Items'].append(comm)

    jsn = get_json()

    r = ses.post(url('task_complete'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r

def add_comment(id, text, file_=None, file_id=None):
    task = Item('TaskId', str(id))
    if file_:
        comm = Item('Comment', None,
                    [Item('Text', str(text)),
                     Item('Attachments', None,
                          dataarray=[Item('Uid', file_upload(file_))]
                   )])
    elif file_id:
        comm = Item('Comment', None,
                    [Item('Text', str(text)),
                     Item('Attachments', None,
                          dataarray=[Item('Uid', file_id)]
                   )])
    else:
        comm = Item('Comment', None, [Item('Text', str(text))])

    d['Items'].append(task)
    d['Items'].append(comm)

    jsn = get_json()

    r = ses.post(url('add_comment'),
                 headers=headers,
                 data=jsn)
    print('>> Response: ' + r.text)
    return r
