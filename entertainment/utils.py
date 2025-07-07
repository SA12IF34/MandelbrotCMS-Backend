import requests
from bs4 import BeautifulSoup
import json
import os
from itertools import islice
from time import sleep
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

    return x['relation'] == 'Sequel'

def filter_pre(x):

    return x['relation'] == 'Prequel'

def get_mal_sequels(data, type_, access_token, collected_ids):
    relations = filter(filter_seq, data['relations'])
    relatives = []
    sleep(1)
    for entry in relations:

        if entry['entry'][0]['type'] == 'music' or entry['entry'][0]['type'] == 'cm':
            continue

        if entry['entry'][0]['mal_id'] in collected_ids:
            continue

        collected_ids.append(entry['entry'][0]['mal_id'])

        res = requests.get(f'https://api.jikan.moe/v4/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}/full/')
        entry_data = res.json()['data']
    
        entry_genres = [*entry_data['genres'], *entry_data['explicit_genres'], *entry_data['themes'], *entry_data['demographics']]

        relatives.append({
            'title': entry['entry'][0]['name'],
            'link': f'https://myanimelist.net/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}',
            'image': entry_data['images']['jpg']['large_image_url'],
            'status': 'future',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['score'],
            'genres':  [x['name'].lower() for x in entry_genres if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': entry["entry"][0]["type"]
        })
        sleep(0.7)

        relatives.extend(get_mal_sequels(entry_data, type_, access_token, collected_ids)[0])
    
    return relatives, collected_ids



def get_mal_prequels(data, type_, access_token, collected_ids):
    relations = filter(filter_pre,data['relations'])
    relatives = []
    sleep(1)
    for entry in relations:

        if entry['entry'][0]['type'] == 'music' or entry['entry'][0]['type'] == 'cm':
            continue

        if entry['entry'][0]['mal_id'] in collected_ids:
            continue

        collected_ids.append(entry['entry'][0]['mal_id'])

        res = requests.get(f'https://api.jikan.moe/v4/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}/full/')
        print(res.json())
        entry_data = res.json()['data']
    
        entry_genres = [*entry_data['genres'], *entry_data['explicit_genres'], *entry_data['themes'], *entry_data['demographics']]

        relatives.append({
            'title': entry['entry'][0]['name'],
            'link': f'https://myanimelist.net/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}',
            'image': entry_data['images']['jpg']['large_image_url'],
            'status': 'done',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['score'],
            'genres':  [x['name'].lower() for x in entry_genres if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': entry["entry"][0]["type"]
        })
        sleep(0.7)

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
        response = requests.get(f'https://api.jikan.moe/v4/anime/{id_}/full/')

        if response.status_code == 401:
            update_tokens(client_id, client_secret, refresh_token)
            return get_mal(link)

        data = response.json()['data']
        subtype = 'anime'
 
        

    if 'manga' in link:
        response = requests.get(f'https://api.jikan.moe/v4/manga/{id_}/full/')

        if response.status_code == 401:
            update_tokens(client_id, client_secret, refresh_token)
            return get_mal(link)

        data = response.json()['data']
        subtype = 'manga'

    genres_list = [*data['genres'], *data['explicit_genres'], *data['themes'], *data['demographics']]

    genres = [x['name'] for x in genres_list if x['name'].lower() in genre_names]
    title = data['title']
    description = data['synopsis']
    rate = data['score']
    image = data['images']['jpg']['large_image_url']
    relatives = []

    for entry in data['relations']:
        sleep(0.7)

        if entry['relation'] == 'Other':
            continue
        
        if entry['entry'][0]['type'] == 'music' or entry['entry'][0]['type'] == 'cm':
            continue

        res = requests.get(f'https://api.jikan.moe/v4/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}/full/')
        entry_data = res.json()['data']


        if entry['relation'] == 'Prequel':
            prequel_relatives = get_mal_prequels(entry_data, 'anime', access_token, [id_])[0]
            relatives.extend(prequel_relatives)

        if entry['relation'] != 'Prequel':
            sequel_relatives = get_mal_sequels(entry_data, 'anime', access_token, [id_])[0]
            relatives.extend(sequel_relatives)
        
        
        entry_genres = [*entry_data['genres'], *entry_data['explicit_genres'], *entry_data['themes'], *entry_data['demographics']]

        relatives.append({
            'title': entry['entry'][0]['name'],
            'link': f'https://myanimelist.net/{entry["entry"][0]["type"]}/{entry["entry"][0]["mal_id"]}',
            'image': entry_data['images']['jpg']['large_image_url'],
            'status': 'done' if entry['relation'] == 'Prequel' else 'future',
            'description': '.' if len(entry_data['synopsis']) == 0 else entry_data['synopsis'],
            'rate': entry_data['score'],
            'genres':  [x['name'].lower() for x in entry_genres if x['name'].lower() in genre_names],
            'type': 'anime&manga',
            'subtype': entry['entry'][0]['type']
        })
    


    return {
        'title': title,
        'description': description,
        'link': link,
        'type': 'anime&manga',
        'subtype': subtype,
        'image': image,
        'rate': float(rate) if rate is not None else None,
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


    # https://store.steampowered.com/api/appdetails?appids=24682 api link

    if '/app/' in link and 'store.steampowered.com' in link:
        link_ = link.split('/')
        id_ = link_[link_.index('app') + 1]

        response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={id_}')
        data = response.json()[id_]['data']

        return {
            'title': data['name'],
            'description': data['short_description'],
            'image': data['header_image'],
            'rate': float(data['metacritic']['score']/10) if 'metacritic' in data else None,
            'genres': [x['description'].lower() for x in data['genres'] if x['description'].lower() in genre_names],
            'type': 'game',
            'subtype': 'game',
            'link': link
        }, []


    return None, []



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

    avg_rate = doc.find_all('rt-text', {'slot': 'audienceScore'})[0].text.strip()
    avg_rate
    avg_rate = int(avg_rate[:-1])/10 if len(avg_rate) > 0 and avg_rate[:-1].isdigit() else None

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


def get_imdb(link):

    link_ = link

    if link.endswith('/'):
        link_ = list(link)
        link_[-1] = ''
        link_ = ''.join(link_)
    
    link_ = link_.split('/')

    if 'title' not in link_:
        return None, []
    
    id_ = link_[link_.index('title') + 1]
    
    response = requests.get(f'http://www.omdbapi.com/?i={id_}&apikey={"9815aa71"}')

    data = response.json()

    if data and 'Response' in data and data['Response'] == 'True':
        return {
            'title': data['Title'],
            'description': data['Plot'],
            'image': data['Poster'],
            'rate': float(data['imdbRating']) if data['imdbRating'] else None,
            'genres': [x.lower() for x in data['Genre'].split(', ') if x.lower() in genre_names],
            'type': 'anime&manga' if data['Language'] == 'Japanese' and 'Japan' in data['Country'] else 'shows&movies',
            'subtype': 'movie' if data['Type'] == 'movie' else 'show',
            'link': link
        }, []







