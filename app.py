from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)

ELASTIC_SEARCH_SERVER = "https://elastic:gg7qKeybI_+e1L3+VK+Q@localhost:9200"
es = Elasticsearch(ELASTIC_SEARCH_SERVER,
                   ca_certs=False,
                   verify_certs=False)


def query_elastic(query_dic):
    print(query_dic)
    match_arr = []
    resp_arr = []
    if query_dic.get('limit') is None:
        size = 25
    else:
        size = query_dic.get('limit')
    if query_dic.get('offset') is None:
        _from = 0
    else:
        _from = query_dic.get('offset')
    if query_dic.get('attribute.name') is not None:
        names = query_dic.get('attribute.name').split(';')
        for name in names:
            dic_ = {"match": {"characteristics.code": name}}
            match_arr.append(dic_)
    if query_dic.get('attribute.value') is not None:
        values = query_dic.get('attribute.value').split(';')
        for value in values:
            dic_ = {"match": {"characteristics.value": value}}
            match_arr.append(dic_)
    if query_dic.get('category.code') is not None:
        values = query_dic.get('category.code').split(';')
        for value in values:
            dic_ = {"match": {"category.code": value}}
            match_arr.append(dic_)

    resp = es.search(index="offers", from_=_from, size=size, query={
        "bool": {
            "must": match_arr
        }
    })

    total_count = resp['hits']['total']['value']
    print(total_count)
    for hit in resp['hits']['hits']:
        resp_arr.append(hit["_source"])

    # pages = int(total_count) / int(size) + 1
    # page = int(_from) / int(size) + 1
    # print(pages)
    # print(page)
    # return render_template('loop.html', offers=resp_arr, page=round(page), pages=round(pages), pg=query_dic)
    r = make_response(jsonify(resp_arr))
    r.headers['X-Total-Count'] = total_count
    x = total_count if int(_from) + int(size) > total_count else int(_from) + int(size)
    r.headers['content-range'] = 'items ' + str(_from) + ' - ' + str(x) + ' / ' + str(total_count)

    return r


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/offerings')
def offerings():  # put application's code here
    args = request.args
    return query_elastic(args)


if __name__ == '__main__':
    app.run()
