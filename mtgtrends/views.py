from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests, json, pandas as pd, io, matplotlib, matplotlib.pyplot as plt, base64
matplotlib.use('Agg')

def index(request):
    params = request.GET.copy()

    # 語句検索
    search_word = request.GET.get('name')
    if search_word:
        res = requests.get('https://upauper63-mtgtrendsapi.herokuapp.com/api/items/?search=' + search_word)
    else:
        res = requests.get('https://upauper63-mtgtrendsapi.herokuapp.com/api/items/')
        search_word = ''

    items = json.loads(res.text)

    # ページネータ処理
    if 'page' in params:
        page = params['page']
        del params['page']
    else:
        page = 1
    search_params = params.urlencode()
    paginator = Paginator(items, 50)
    try:
        items = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        items = paginator.page(1)

    return TemplateResponse(request, 'mtgtrends/index.html', {'items': items, 'search_params': search_params, 'search_word': search_word})


def detail(request, item_id):
    res = requests.get('https://upauper63-mtgtrendsapi.herokuapp.com/api/item/?id=' + str(item_id))
    item = json.loads(res.text)
    df = pd.DataFrame(item[0]['trends'], columns=['Date', 'Price'])
    df.plot(x="Date", y="Price", ylabel='Price', rot=30, marker="o", legend=None)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    svg = buf.getvalue()
    graph = base64.b64encode(svg).decode('utf-8')
    buf.close()
    plt.cla()
    return TemplateResponse(request, 'mtgtrends/detail.html', {'graph': graph, 'name': item[0]['name']})