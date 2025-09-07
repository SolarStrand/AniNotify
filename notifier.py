from gui import App
from anime_parsers_ru import KodikParserAsync
import asyncio
import sys
from PyQt6.QtWidgets import QApplication
import time
from winotify import Notification, audio

parser = KodikParserAsync()
toast = Notification(
    app_id="AniNotify",
    title="Новая озвучка",
    msg="Была найдена новая озвучка!"
)
toast.set_audio(audio.Default, loop=False)
id_type = 'shikimori'

# async def get_anime_episode(name, season):
#     try:
#         result = await parser.search(title=f"{name} [ТВ-{season}]")
#         only_names = [title['title'] for title in result]
#         IDs = [i['shikimori_id'] for i in result]
#         primary_id = IDs[0]
#         info = await parser.get_info(id=primary_id, id_type='shikimori')
#         only_voices = [i['name'] for i in info['translations'] if i['type'] == 'Озвучка']
#         return only_names, only_voices
#     except:
#         window.display_message()

async def get_title_list(name):
    result = await parser.search(title=name)
    titles = [title['title'] for title in result]
    IDs = [id[f'{id_type}_id'] for id in result]
    return titles, IDs
    
async def get_voice_list(id, current=None):
    info = await parser.get_info(id=id, id_type=id_type)
    all_voices = [i['name'] for i in info['translations']]
    if current:
        current_voices = [i for i in all_voices if i in current]
        return current_voices
    return all_voices

        
def check_for_new(checklist):
    while True:
        check = asyncio.run(get_voice_list(id, voices))
        if checklist != check:
            if data['notification'] == 'true':
                window.display_message(head='Ура!', msg='Озвучка была обновлена!')
            toast.show()
            window.change_example(check)
            break
        print(f"original : {checklist}")
        print(F"current : {check}")
        time.sleep(120)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    exit_code = app.exec()
    data = window.get_saved_data()
    print(data)
    name = data['name']
    voices = data['voices']
    id = data['id']
    time.sleep(1)
    if data['example'] is None:
        print('example is None')
        example = asyncio.run(get_voice_list(id, sorted(voices)))
        window.change_example(example)
    else:
        print('already have example')
        example = data['example']
    check_for_new(example)

    # last
    sys.exit(exit_code)
    
    