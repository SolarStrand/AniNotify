from anime_parsers_ru import KodikSearch, KodikParser
import asyncio

kodik = KodikSearch()
print(KodikParser.get_token())
id_type = 'Shikimori'

def get_voice_list():
    query = kodik.title('Наруто')
    data = query.execute()
    print(data)

get_voice_list()