from util import data_io

from doccano_api import purge, create_project, create_user
admin_id=1
if __name__ == '__main__':
    purge()
    for a in data_io.read_jsonl('annotators.jsonl'):
        create_user(a['name'],a['password'],a['id'])
        create_project(project_name=a['name'] + '_project', users=[admin_id,a['id']])