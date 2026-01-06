from anime_parsers_ru import KodikParser
import asyncio

parser = KodikParser(validate_token=False)
parser.TOKEN = parser.get_token()
id_type = 'Shikimori'

def get_voice_list():
    info = parser.search("Наруто")
    titles = [title['title'] for title in info]
    print(titles)

get_voice_list()