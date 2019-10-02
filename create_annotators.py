from password_generator import PasswordGenerator
from util import data_io

if __name__ == '__main__':
    pwo = PasswordGenerator()
    pwo.minlen=9
    pwo.maxlen=9
    def build_user(eid,user_name):
        return {'name':user_name,
                'password': pwo.generate(),
                'id':eid
                }
    data_io.write_jsonl('annotators.jsonl',(build_user(k+2,user_name) for k,user_name in enumerate(['Salar','Vinicius','Tarcisio','Tilo'])))
