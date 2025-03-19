import requests
from bs4 import BeautifulSoup
import json
import os
from itertools import islice

from django.conf import settings


def read_json():
    try:
        with open(os.path.join(settings.BASE_DIR, 'entertainment/tokens.json'), 'r') as f:
            data = json.load(f)
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            return access_token, refresh_token

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing tokens.json: {e}")
        return None, None

def write_json(data):

    with open(os.path.join(settings.BASE_DIR, 'entertainment/tokens.json'), 'w') as f:
        json.dump(data, f, indent=2)

    print('wrote json')
    return

def update_tokens(client_id, client_secret, refresh_token):
    new_tokens = requests.post('https://myanimelist.net/v1/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token':refresh_token
    }).json()

    write_json(new_tokens)
    return

genre_names = ['action', 'adventure', 'ai', 'arts', 'cars', 'comedy', 'dementia',
    'demons', 'drama', 'ecchi', 'fantasy', 'sci-fi', 'game', 'harem',
    'hentai', 'historical', 'horror', 'josei', 'kids', 'life', 'magic',
    'martial', 'mecha', 'military', 'music', 'mystery', 'parody',
    'police', 'power', 'psychological', 'romance', 'samurai', 'school',
    'seinen', 'shoujo', 'shounen', 'slice', 'space', 'sports',
    'super', 'supernatural', 'thriller', 'vampire', 'yaoi', 'yuri', 
    'cgdct', 'iyashikei', 'moe', 'slice of life']


def filter_seq(x):

    return x['relation_type'] == 'sequel'

def filter_pre(x):

    return x['relation_type'] == 'prequel'

def get_mal_sequels(data, type_, access_token, collected_ids):
    relations = filter(filter_seq,data['related_anime' if type_ == 'anime' else 'related_manga'])
    relatives = []

    for entry in relations:

        if entry['node']['id'] in collected_ids:
            continue

        collected_ids.append(entry['node']['id'])

        res = requests.get(f'https://api.myanimelist.net/v2/{type_}/{entry["node"]["id"]}?fields=title,main_picture,synopsis,genres,mean,media_type,related_{type_}', headers={
        'Authorization': 'Bearer '+access_token
        })

        entry_data = res.json()

        if entry_data['media_type'] == 'music' or entry_data['media_type'] == 'cm':
            continue

        relatives.append({
            'title': entry['node']['title'],
            'link': f'https://myanimelist.net/{type_}/{entry["node"]["id"]}',
            'image': entry['node']['main_picture']['medium'],
            'status': 'future',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['mean'] if 'mean' in entry_data.keys() else None,
            'genres':  [x['name'].lower() for x in entry_data['genres'] if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': type_
        })

        relatives.extend(get_mal_sequels(entry_data, type_, access_token, collected_ids)[0])
    
    return relatives, collected_ids



def get_mal_prequels(data, type_, access_token, collected_ids):
    relations = filter(filter_pre,data['related_anime' if type_ == 'anime' else 'related_manga'])
    relatives = []

    for entry in relations:

        if entry['node']['id'] in collected_ids:
            continue

        collected_ids.append(entry['node']['id'])

        res = requests.get(f'https://api.myanimelist.net/v2/{type_}/{entry["node"]["id"]}?fields=title,main_picture,synopsis,genres,mean,media_type,related_{type_}', headers={
        'Authorization': 'Bearer '+access_token
        })

        entry_data = res.json()

        if entry_data['media_type'] == 'music' or entry_data['media_type'] == 'cm':
            continue

        relatives.append({
            'title': entry['node']['title'],
            'link': f'https://myanimelist.net/{type_}/{entry["node"]["id"]}',
            'image': entry['node']['main_picture']['medium'],
            'status': 'done',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['mean'] if 'mean' in entry_data.keys() else None,
            'genres':  [x['name'].lower() for x in entry_data['genres'] if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': type_
        })

        relatives.extend(get_mal_prequels(entry_data, type_, access_token, collected_ids)[0])
    
    return relatives, collected_ids

def get_mal(link):
    
    if link.endswith('/'):
        link = list(link)
        link[-1] = ''
        link = ''.join(link)

    link_list = link.split('/')

    if link_list[-1].isdigit():
        id_ = link_list[-1]
    else:
        id_ = link.split('/')[-2]

    access_token, refresh_token = read_json()
    if access_token is None or refresh_token is None:
        return

    client_id = settings.ENV('MAL_CLIENT_ID')
    client_secret = settings.ENV('MAL_CLIENT_SECRET')

    
    if 'anime' in link:
        response = requests.get(f'https://api.myanimelist.net/v2/anime/{id_}?fields=title,main_picture,synopsis,genres,mean,related_anime,related_manga,media_type', headers={
        'Authorization': 'Bearer '+access_token
        })

        if response.status_code == 401:
            update_tokens(client_id, client_secret, refresh_token)
            return get_mal(link)

        data = response.json()
        subtype = 'anime'
 
        

    if 'manga' in link:
        response = requests.get(f'https://api.myanimelist.net/v2/manga/{id_}?fields=title,main_picture,synopsis,genres,mean,related_anime,related_manga,media_type', headers={
        'Authorization': 'Bearer '+access_token
        })

        if response.status_code == 401:
            update_tokens(client_id, client_secret, refresh_token)
            return get_mal(link)

        data = response.json()
        subtype = 'manga'
        
    genres = [x['name'] for x in data['genres'] if x['name'].lower() in genre_names]
    title = data['title']
    description = data['synopsis']
    rate = data['mean']
    image = data['main_picture']['medium']
    relatives = []
    
    for entry in data['related_anime']:
        res = requests.get(f'https://api.myanimelist.net/v2/anime/{entry["node"]["id"]}?fields=title,main_picture,synopsis,genres,mean,media_type,related_anime', headers={
        'Authorization': 'Bearer '+access_token
        })

        if entry['relation_type'] == 'other':
            continue
        
        entry_data = res.json()        
        if entry_data['media_type'] == 'music' or entry_data['media_type'] == 'cm':
            continue

        if entry['relation_type'] == 'prequel':
            prequel_relatives = get_mal_prequels(entry_data, 'anime', access_token, [id_])[0]
            relatives.extend(prequel_relatives)

        if entry['relation_type'] != 'prequel':
            sequel_relatives = get_mal_sequels(entry_data, 'anime', access_token, [id_])[0]
            relatives.extend(sequel_relatives)

        relatives.append({
            'title': entry['node']['title'],
            'link': f'https://myanimelist.net/anime/{entry["node"]["id"]}',
            'image': entry['node']['main_picture']['medium'],
            'status': 'done' if entry['relation_type'] == 'prequel' else 'future',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['mean'] if 'mean' in entry_data.keys() else None,
            'genres':  [x['name'].lower() for x in entry_data['genres'] if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': 'anime'
        })
    
    for entry in data['related_manga']:
        res = requests.get(f'https://api.myanimelist.net/v2/manga/{entry["node"]["id"]}?fields=title,main_picture,synopsis,genres,mean,media_type,related_manga', headers={
        'Authorization': 'Bearer '+access_token
        })
        
        if entry['relation_type'] == 'other':
            continue

        entry_data = res.json()   

        if entry['relation_type'] == 'prequel':
            prequel_relatives = get_mal_prequels(entry_data, 'manga', access_token, [id_])[0]
            relatives.extend(prequel_relatives)

        else:
            sequel_relatives = get_mal_sequels(entry_data, 'manga', access_token, [id_])[0]
            relatives.extend(sequel_relatives)

        relatives.append({
            'title': entry['node']['title'],
            'link': f'https://myanimelist.net/manga/{entry["node"]["id"]}',
            'image': entry['node']['main_picture']['medium'],
            'status': 'done' if entry['relation_type'] == 'prequel' else 'future',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['mean'] if 'mean' in entry_data.keys() else None,
            'genres':  [x['name'].lower() for x in entry_data['genres'] if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': 'manga',
            'mal_id': entry['node']['id']
        })

    return {
        'title': title,
        'description': description,
        'link': link,
        'type': 'anime&manga',
        'subtype': subtype,
        'image': image,
        'rate': float(rate),
        'genres': genres,
        'mal_id': id_
    }, relatives
    

def get_anilist(link):
    if link.endswith('/'):
        link = list(link)
        link[-1] = ''
        link = ''.join(link)

    link = link.split('/')
    id_ = link[-1] if link[-1].isdigit() else link[-2] if link[-2].isdigit() else link[-3]
    link = '/'.join(link)

    query = '''
    query ($id: Int) {
        Media (id: $id) {
            id
            title {
                romaji
            }
            description(asHtml: false)
            meanScore
            genres
            coverImage {
                large
            }
            idMal
            type
            format
            startDate {
                year
            }
            relations {
                nodes {
                    id
                    title {
                    romaji
                    }
                    genres
                    description(asHtml: false)
                    coverImage {
                    large
                    }
                    meanScore
                    idMal
                    type
                    format
                    startDate {
                        year
                    }
                }
            }
                
        }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'id': id_
    }

    api_link = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    response = requests.post(api_link, json={'query': query, 'variables': variables})
    data = response.json()['data']['Media']
    print(float(data['meanScore']/10))
    date_ = int(data['startDate']['year'])
    return_data = {
    'title' : data['title']['romaji'],
    'description' : data['description'],
    'rate' : float(int(data['meanScore'])/ 10),
    'genres' : [x.lower() for x in data['genres'] if x.lower() in genre_names],
    'image' : data['coverImage']['large'],
    'mal_id' : data['idMal'],
    'type': 'anime&manga',
    'subtype' : data['type'].lower(),
    'date_' : date_,
    'link': link
    }

    relatives = []

    for entry in data['relations']['nodes']:
        if entry['format'] not in ['TV', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MANGA', 'NOVEL', 'ONE_SHOT']:
            continue

        status_condition_1 = int(entry['startDate']['year']) < date_
        status_condition_2 = entry['format'] == 'TV' or entry['format'] == 'MOVIE'

        relatives.append({
            'title': entry['title']['romaji'],
            'description': entry['description'],
            'genres': [x.lower() for x in entry['genres'] if x.lower() in genre_names],
            'image': entry['coverImage']['large'],
            'rate': float(int(entry['meanScore'])/ 10),
            'mal_id': entry['idMal'],
            'type': 'anime&manga',
            'subtype': entry['type'].lower(),
            'status': 'done' if status_condition_1 and status_condition_2 else 'future',
            'link': f'https://anilist.co/{entry["type"].lower()}/{entry["id"]}/'
        })

    return return_data, relatives


def get_steam(link): # Scrapes game data from Steam.

    page = requests.get(link).text

    doc = BeautifulSoup(page, 'html.parser')

    class_name = 'apphub_AppName'

    name = doc.find('div', class_=class_name).string

    descriptions = doc.find('div', class_='game_area_description').strings
    description = next(islice(descriptions,2, 3)).strip()
    
    image = doc.find('img', class_='game_header_image_full').attrs.get('src')

    return {
        'title': name,
        'description': description,
        'image': image,
        'type': 'game',
        'subtype': 'game',
        'link': link
    }, []


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def get_rottentomatoes(link):
    
    page = requests.get(link, headers=headers).text
    doc = BeautifulSoup(page, 'html.parser')

    title = doc.find('h1', id='media-hero-label')
    title = title.find('sr-text').text.strip()

    description_container = doc.find('div', {'slot': 'description'})
    description = description_container.find('rt-text', {'slot': 'content'}).text.strip()

    img = doc.find('rt-img', {'slot': 'posterImage'}).attrs.get('src')

    avg_rate = doc.find('rt-text', {'slot': 'audienceScore'}).text.strip()
    avg_rate = int(avg_rate[:-1])/10

    genres = doc.find_all('rt-text', {'slot': 'metadataGenre'})
    genres_list = []
    for g in genres:
        if g.text.strip().lower() in genre_names:
            genres_list.append(g.text.strip().lower())

    language = doc.find(lambda tag: tag.name == 'dt' and 'language' in tag.text.lower())
    language = language.find_next_sibling('dd').find('rt-text').text.strip()
    if 'english' in language.lower():
        type = 'shows&movies'
    
    elif 'japanese' in language.lower():
        type = 'anime&manga'

    if type == 'anime&manga':
        if '/tv/' in link:
            subtype = 'show'
        elif '/m/' in link:
            subtype = 'movie' 

    elif type == 'shows&movies':
        subtype = 'anime'


    return {
        'title': title,
        'description': description,
        'image': img,
        'rate': avg_rate,
        'genres': genres_list,
        'type': type,
        'subtype': subtype,
        'link': link
    }, []
    



