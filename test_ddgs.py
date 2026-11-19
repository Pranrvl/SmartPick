from duckduckgo_search import DDGS
import time

ddgs = DDGS()
queries = [
    'Xiaomi Redmi Note 13 Pro Plus',
    'Realme GT 6',
    'Vivo V30',
    'iQOO 12',
    'Samsung Galaxy S24'
]

for q in queries:
    try:
        res = list(ddgs.images(q + ' smartphone', max_results=1))
        if res:
            print(q, '->', res[0]['image'])
        else:
            print(q, '-> NO RESULT')
        time.sleep(1)
    except Exception as e:
        print(q, '-> ERROR:', e)
