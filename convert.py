import argparse
import json
import requests

WUNDERLIST_API_PREFIX = 'https://a.wunderlist.com/api/v1/'

parser = argparse.ArgumentParser(description='Parses Asana tasks dumped to a json file and adds them to Wunderlist via API.')
parser.add_argument('access_token', help='Wunderlist access token which can be retrieved from https://developer.wunderlist.com/apps')
parser.add_argument('client_id', help='Wunderlist client id which can be retrieved from https://developer.wunderlist.com/apps')
parser.add_argument('asana_file', help='JSON file of Asana tasks dumped by selecting a project and choosing Export > JSON')
parser.add_argument('--list', help='Optional Wunderlist task list name to add tasks to. Defaults to "Asana"', default='Asana')
args = parser.parse_args()

s = requests.Session()
s.headers.update({'X-Access-Token': args.access_token,
                  'X-Client-ID': args.client_id})
s.verify = True

r = s.get(WUNDERLIST_API_PREFIX + 'users')
print('Hi ' + r.json()[0]['name'] + '!')

r = s.get(WUNDERLIST_API_PREFIX + 'lists')
lists = r.json()
titles = [l['title'] for l in lists]
list_name = args.list
print('Found lists: ' + str(titles))
if not list_name in titles:
    print('Creating new list:' + list_name)
    r = s.post(WUNDERLIST_API_PREFIX + 'lists', json={'title': list_name})
    list_id = r.json()['id']
else:
    list_id = lists[titles.index(list_name)]['id']

with open('data.json') as f:
    data = json.load(f)

def passes_filter(task):
    if (len(task['name']) > 255):
        print('WARNING Task name is longer than 255: ' + task['name'])
        raise

    return task['completed'] == False

def traverse(task_f, subtask_f):
    for t in data['data']:
        if not passes_filter(t):
            continue
        task_f(t)
        for s in t['subtasks']:
            if not passes_filter(s):
                continue
            subtask_f(s, t)

print('These are your tasks:')
def p(t):
    print(t['name'])
def p1(t, s):
    print('    ' + t['name'])
traverse(p, p1)

tasks = s.get(WUNDERLIST_API_PREFIX + 'tasks', params={'list_id': list_id}).json()
task_names = [t['title'] for t in tasks]
task_map = {}
for t in tasks:
    task_map[t['title']] = t['id']

subtasks = s.get(WUNDERLIST_API_PREFIX + 'subtasks', params={'list_id': list_id}).json()
subtask_map = {}
for subtask in subtasks:
    if not subtask['task_id'] in subtask_map:
        subtask_map[subtask['task_id']] = []
    subtask_map[subtask['task_id']].insert(0, subtask['title'])

def createTask(task):
    if (task['name'] in task_names):
        print('Skipping: ' + task['name'])
        return
    r = s.post(WUNDERLIST_API_PREFIX + 'tasks', json={'list_id': list_id, 'title': task['name']})
    o = r.json()
    task_map[task['name']] = o['id']
def createSubtask(subtask, task):
    task_id = task_map[task['name']]
    if task_id in subtask_map and subtask['name'] in subtask_map[task_id]:
        print('Skipping subtask: ' + subtask['name'])
        return
    r = s.post(WUNDERLIST_API_PREFIX + 'subtasks', json={'task_id': task_id , 'title': subtask['name']})
    o = r.json()
traverse(createTask, createSubtask)

# TODOs:
# - Copy other fields like due-date
# - Allow duplicate subtasks and/or tasks
