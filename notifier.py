from gui import App, WindowsStartupManager
from anime_parsers_ru import KodikParserAsync
import asyncio
import sys
from PyQt6.QtCore import QWaitCondition, QMutex, QObject
from PyQt6.QtWidgets import QApplication
import time
from winotify import Notification, audio
import threading

class Background(QObject):
    def __init__(self):
        super().__init__()
        self.condition = QWaitCondition()
        self.mutex = QMutex()
        self.should_stop = False
        self.main_thread = None
        self.sleep_seconds = 300

    def start(self,checklist,voices,id,notification,window):
        self.should_stop = False
        self.main_thread = threading.Thread(
            target=self._run,
            args=(checklist,voices,id,notification,window),
            daemon=True
        )
        self.main_thread.start()


    def _run(self, checklist, voices, id, notification,window):
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # try:
        while not self.should_stop:
            check = asyncio.run(get_voice_list(id,voices))
            if checklist != check:
                if notification == 'true':
                    window.display_message(head='Ура!', msg=f'Озвучка была обновлена!')
                try:
                    toast.msg += f"\n{next(iter(set(check) - set(checklist), 'Error'))}"
                except:
                    window.display_message(msg='Попробуйте изменить параметры и попробовать снова')
                toast.show()     
                window.change_example(check)
                break
            print(f"original : {checklist}")
            print(F"current : {check}")
            self.mutex.lock()
            self.condition.wait(self.mutex, self.sleep_seconds*1000)
            self.mutex.unlock()

            if self.should_stop:
                print('Actually stopped thread')
                # could also emit a signal to tell gui to reverse buttons, but well
                break
        # finally:
        #     loop.close()
    def stop_thread(self):
        self.should_stop = True
        self.condition.wakeAll()
        print('Stopped thread')
        


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

def start_search(window):
    data = window.get_saved_data()
    print(data)
    voices = data['voices']
    id = data['id']
    notification = data['notification']
    time.sleep(1)
    if data['example'] is None:
        print('example is None')
        example = asyncio.run(get_voice_list(id, sorted(voices)))
        window.change_example(example)
    else:
        print('already have example')
        example = data['example']
    
    bg.start(example,voices,id,notification,window)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    bg = Background()
    startup_manager = WindowsStartupManager("AniNotify")

    window.search_started_signal.connect(lambda: start_search(window))
    window.stop_search_signal.connect(lambda: bg.stop_thread())
    if not window.saved_startup_bool:
        window.show()
    else:
        # window.setup_tray()
        window.stop_thread_button.setEnabled(True)
        window.connect_button.setEnabled(False)
        window.start_search_action.setEnabled(False)
        window.stop_search_action.setEnabled(True)
        start_search(window)
    sys.exit(app.exec())


    # after close change that
    # data = window.get_saved_data()
    # print(data)
    # name = data['name']
    # voices = data['voices']
    # id = data['id']
    # time.sleep(1)
    # if data['example'] is None:
    #     print('example is None')
    #     example = asyncio.run(get_voice_list(id, sorted(voices)))
    #     window.change_example(example)
    # else:
    #     print('already have example')
    #     example = data['example']
    # check_for_new(example)

    # last
    
    