import pymongo
from bson.json_util import dumps
import json


def get_rent_data(params):
    client = pymongo.MongoClient('mongodb://root:example@localhost:27017/')
    db = client['591rent']
    collections = db['on_sale']
    query = params
    result = list(collections.find(query))
    print(f'params is: {params}, counts={len(result)}')
    return json.loads(dumps(result))
    # return dumps(list(result)).encode('BIG5')


if __name__ == '__main__':

    params = {
        'role_name': '屋主',
        'linkman': '王先生',
    }

    # params = InputParam()
    # params.role_name = '屋主'

    data = get_rent_data(params)
    print(data)
