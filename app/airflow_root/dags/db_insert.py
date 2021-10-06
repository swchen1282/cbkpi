import pymongo

CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/myFirstDatabase"


def mongo_insert(obj: list) -> dict:
    """
    Insert obj(list of dicts) into mongo
    :param obj: list of dicts
    :return: dict
    """
    try:
        client = pymongo.MongoClient('mongodb://root:example@localhost:27017/')
        db = client['591rent']
        collections = db['on_sale']
        collections.insert_many(obj)
        return {'result': 0, 'msg': 'insert successfully'}
    except Exception as e:
        raise
        # return {'result': 1, 'msg': f'insert fail, exceptions: {e}'}


def mongo_query(params: dict):
    client = pymongo.MongoClient('mongodb://root:example@localhost:27017/')
    db = client['591rent']
    collections = db['on_sale']
    query = params
    result = collections.find(query)

    print(f'params is: {params}, counts={result.count()}')


if __name__ == '__main__':
    params = {
        'role_name': '屋主',
        'linkman': '',
    }
    mongo_query(params)
