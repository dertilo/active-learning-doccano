from pprint import pprint

from sqlalchemy import select
from sqlutil.sqlalchemy_methods import get_sqlalchemy_base_engine, get_tables_by_reflection,get_rows

from data_util import convert_to_doccano
from doccano_api import list_users, create_documents, list_projects, purge_project_documents


def get_user_id(user_name:str):
    users = [u for u in list_users() if u['username']==user_name]
    if len(users)>0:
        return users[0]['id']
    else:
        return None

if __name__ == '__main__':
    sqlalchemy_base,sqlalchemy_engine = get_sqlalchemy_base_engine(host='gunther')
    table = get_tables_by_reflection(sqlalchemy_base.metadata,sqlalchemy_engine)['scierc']
    user_name = 'Tilo'
    user_id = get_user_id(user_name)
    project_id = [p['id'] for p in list_projects() if user_id in p['users']][0]
    purge_project_documents(project_id)

    with sqlalchemy_engine.connect() as conn:
        q = select([table]).limit(5)
        docs = list(get_rows(conn, q))
        doccano_docs = [convert_to_doccano(d) for d in docs]
        pprint(doccano_docs)
        create_documents(doccano_docs,project_id,user_id)