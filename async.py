import requests
import json
import time
import csv
import os
import asyncio
import aiohttp
import fake_useragent

headers = {
    'user-agent': fake_useragent.UserAgent().random,
}

def get_pages(data):
    count = 0
    count_childs = 0
    for i in data:     
        if 'childs' in data[count]:
            for j in data[count]['childs']:
                if 'childs' in data[count]['childs'][count_childs]:
                    for j in data[count]['childs'][count_childs]['childs']:
                        data[count]['childs'].append(j)
                    del data[count]['childs'][count_childs]
                if 'seo' in data[count]['childs'][count_childs]:
                    print(f"\n[Page Name] - {data[count]['childs'][count_childs]['seo']} [URL]  - https://www.wildberries.ru{data[count]['childs'][count_childs]['url']}")
                    header = data[count]['childs'][count_childs]['seo']
                else:
                    print(f"\n[Page Name] - {data[count]['childs'][count_childs]['name']} [URL] - https://www.wildberries.ru{data[count]['childs'][count_childs]['url']}")
                    header = data[count]['childs'][count_childs]['name']
                if 'query' in data[count]['childs'][count_childs]:
                    query = data[count]['childs'][count_childs]['query']
                else:
                    query = '[Query is not found]'
                if 'shard' in data[count]['childs'][count_childs]:
                    shard = data[count]['childs'][count_childs]['shard']
                else: 
                    shard = '[Shard is not found]'
                if 'name' in data[count]:
                    fold_name = data[count]['name']
                else:
                    fold_name = 'Unkown_Object'
                count_childs += 1
                asyncio.run(get_page_ondata(shard, query, header, fold_name))

        count_childs = 0
        count += 1

async def get_page_ondata(shard, query, header, fold_name):
    product = []
    start = time.time()
    url = (f'https://catalog.wb.ru/catalog/{shard}/v4/filters?appType=1&curr=rub&dest=-1221148,-145454,-1430613,-5827642&emp=0&lang=ru&locale=ru&regions=80,64,83,4,38,33,70,69,86,30,40,48,1,66,31,22,113&sort=popular&spp=0&{query}')
    try:
        async with aiohttp.ClientSession() as session:
            req = await session.get(url, headers = headers)
            number_product = int((json.loads(await req.text()))['data']['total']/100 + 1)
            if number_product > 100:
                number_product = 100
            print(f'[System] CONNECT SUCCESS\n[System] Found - {number_product} pages')
            tasks = []
            for count in range(1, number_product+1):
                task = asyncio.create_task(get_pagedata(session, count, shard, query, product))
                tasks.append(task)

            await asyncio.gather(*tasks)
    except:
        pass

    end = time.time()
    print(f'[INFO] Time to work - {end-start}')
        
    save_on_csv(header, fold_name, product)



async def get_pagedata(session, count, shard, query, product):    
    link = (f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1221148,-145454,-1430613,-5827642&emp=0&lang=ru&locale=ru&page={count}&regions=80,64,83,4,38,33,70,69,86,30,40,48,1,66,31,22,113&sort=popular&spp=0&{query}')
    try:
        async with session.get(link, headers=headers, timeout=20) as resp:
            try:
                data = json.loads(await resp.text())
                for i in range((len(data['data']['products']))):
                        name = data['data']['products'][i]['name']
                        brand = data['data']['products'][i]['brand']
                        id = data['data']['products'][i]['id']
                        price = str((data['data']['products'][i]['salePriceU']))[:-2]
                        feedbacks = data['data']['products'][i]['feedbacks']
                        url = f'https://www.wildberries.ru/catalog/{id}/detail.aspx?targetUrl=GP'
                        
                        product.append({'Название': name,
                                    'Бренд': brand,
                                    'Id': id,
                                    'Стоимость': price,
                                    'Кол-во отзывов': feedbacks,
                                    'Ссылка': url})
            except:
                print(await resp.code(), link)
    except:
        pass
        
    

def save_on_csv(name, fold_name, product):
    name = name.replace('/', '.')
    if os.path.isdir(fold_name):
        pass
    else:
        os.mkdir(fold_name)
    with open(f'{fold_name}/{name}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название',
                'Бренд',
                'Id',
                'Стоимость',
                'Кол-во отзывов',
                'Ссылка'
            )
                        )
        for i in range(len(product)):
            writer.writerow(
            (
                product[i]['Название'],
                product[i]['Бренд'],
                product[i]['Id'],
                product[i]['Стоимость'],
                product[i]['Кол-во отзывов'],
                product[i]['Ссылка']
            )
            )
        file.close() 
    print(f'Файл сохранен в {os.getcwd()}\{fold_name}\{name}')


def main():
    category = []
    count1 = 1
    # start = time.time() 
    r = requests.get('https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru.json', headers=headers)
    data = json.loads(r.text)
    for i in data:
        category.append(i['name'])
        print(f'{count1}.{i["name"]}')
        count1 += 1
    count1 = 1
    input_catalog = int(input('''\t\tЯ - парсер сайта WildBerries.
\tЯ умею собирать данные о различных товарах из выбранной Вами категории.\n\nВыберите один раздел из предложенных.\nВведите <0>, чтобы спарсить всё.'''))
    if input_catalog != 0:
        data = [data[input_catalog-1]]
        if 'childs' in data[0]:
            for i in (data[0]['childs']):
                print(f'{count1}.{i["name"]}')
                count1 += 1
        else:
            print('[SYSTEM] Not found')
        input_category = int(input(f'\nВыбран раздел - {(data[0]["name"])}\nВыберите конкретную категорию из каталога.\nВведите <0>, чтобы спарсить всё.'))
        if input_category == 0:
            pass
        else:
            childs = data[0].pop('childs')
            data[0]['childs'] = [childs[input_category-1]]
    elif input_catalog == 0:
        pass
    get_pages(data)

if __name__ == '__main__':
    main()