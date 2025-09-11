from anime_parsers_ru import KodikParserAsync
import asyncio

parser = KodikParserAsync()

async def test():
    result = await parser.search(title="Необъятный океан", include_material_data=True)
    title_list = [title['title'] for title in result]
    grand_blue_2 = [i for i in result if i['title'] == 'Необъятный океан [ТВ-2]'] # shikimori id = 59986
    anime_info = await parser.get_info(id='59986', id_type="shikimori")
    only_voices = anime_info['translations']
    only_ancord = [i for i in only_voices if 'Ancord' in i['name']]
    print(title_list)


asyncio.run(test())