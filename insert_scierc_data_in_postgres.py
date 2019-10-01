import json

from sqlalchemy import Column, String, Table
from sqlutil.sqlalchemy_methods import get_sqlalchemy_base_engine, get_tables_by_reflection, insert_or_update
from util import data_io
from util.data_io import download_data


def scierc_to_postgres(postgres_host,scierc_file:str):
    sqlalchemy_base, sqlalchemy_engine = get_sqlalchemy_base_engine(host=postgres_host)
    data = data_io.read_jsonsl(scierc_file)
    data = ({**{'id': json.dumps(d.pop('doc_key'))}, **d} for d in data)
    data = (d for d in data if isinstance(d['id'], str))
    tables = get_tables_by_reflection(sqlalchemy_base.metadata, sqlalchemy_engine)
    table_name = 'scierc'
    if table_name in tables:
        table = tables[table_name]
        if from_scratch:
            table.drop(sqlalchemy_engine)
            table = None
    else:
        table = None
    if table is None:
        columns = [Column('id', String, primary_key=True)] + [Column(colname, String) for colname in
                                                              ['sentences', 'ner', 'relations', 'clusters']]
        table = Table(table_name, sqlalchemy_base.metadata, *columns, extend_existing=True)
        print('creating table %s' % table.name)
        table.create()

    def update_fun(val, old_row):
        d = {k: json.dumps({'annotator_luan': v}) for k, v in val.items() if k != 'sentences'}
        d['sentences'] = json.dumps(val['sentences'])
        return d

    with sqlalchemy_engine.connect() as conn:
        insert_or_update(conn, table, ['sentences', 'ner', 'relations', 'clusters'], data, update_fun=update_fun)


if __name__ == '__main__':
    from_scratch = True
    ip = 'localhost'
    download_data('http://nlp.cs.washington.edu/sciIE/data','sciERC_processed.tar.gz','data',unzip_it=True)
    file = 'data/processed_data/json/train.json'
    scierc_to_postgres(ip,file)