import sys
import os
from PyQt6.QtGui import QFontMetrics, QIcon, QAction
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QCheckBox, QSpacerItem, QListWidget, QAbstractItemView, QSystemTrayIcon, QMenu, QTextEdit
)
import asyncio
import time
from anime_parsers_ru import KodikParserAsync
import winreg

class StdoutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.setWindowTitle("Debug")

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
    
    def append_text(self,text):
        self.text_edit.append(text)
    
class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self,text):
        self.text_written.emit(str(text))
    
    def flush(self):
        pass

class WindowsStartupManager:
    def __init__(self, app_name):
        self.app_name = app_name
        self.registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
    def enable_startup(self):
        """Enable application to run on startup"""
        try:
            # Get the path to the current executable
            exec_path = os.path.abspath(sys.argv[0])
            
            # Open the registry key for current user startup programs
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_path,
                0, winreg.KEY_SET_VALUE
            )
            
            # Set the value
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'"{exec_path}"')
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False
            
    def disable_startup(self):
        """Disable application from running on startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_path,
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # Key doesn't exist, which means it's already disabled
            return True
        except Exception as e:
            print(f"Error disabling startup: {e}")
            return False

class App(QWidget):
    relative_path = "bin/aninotify_icon.ico"
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    icon_path = os.path.join(base_path,relative_path)
    search_started_signal = pyqtSignal()
    stop_search_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings('Solar','AniNotify')
        self.search_example = self.settings.value('example', None)
        self.parser = KodikParserAsync()
        self.id_type = 'shikimori'
        self.startup_manager = WindowsStartupManager("AniNotify")
        self.search_bool = False
        self.output_window = StdoutWindow()
        self.stream = EmittingStream()
        self.stream.text_written.connect(self.output_window.append_text)
        sys.stdout = self.stream
        self.setup_tray()
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.setWindowTitle("AniNotify")
        self.setGeometry(300,300,500,200)
        self.setMaximumSize(500,200)
        self.setWindowIcon(QIcon(self.icon_path))
        space = QSpacerItem(30,15)
        
        layout = QVBoxLayout()

        label = QLabel("Примечание : Программу нужно использовать по порядку, начиная сверху.\nНе нужно каждый раз сохранять, только в случае изменения параметров.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addSpacerItem(space)
        #
        # anime name line 
        #
        label_input_layout_name = QHBoxLayout()

        label = QLabel("Название аниме : ")

        self.anime_name_input = QLineEdit()
        self.anime_name_input.setPlaceholderText("Просто название, без сезона")

        label_input_layout_name.addWidget(label)
        label_input_layout_name.addWidget(self.anime_name_input)
        label_input_layout_name.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(label_input_layout_name)
        #
        # season line
        #
        # label_input_layout_season = QHBoxLayout()

        # label = QLabel("Сезон : ")

        # self.season_counter = QComboBox()
        # self.season_counter.addItems([str(i) for i in range(1, 51)])
        # self.season_counter.setFixedWidth(50)

        # label_input_layout_season.addWidget(label)
        # label_input_layout_season.addWidget(self.season_counter)
        # label_input_layout_season.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # layout.addLayout(label_input_layout_season)

        # button

        button_layout = QHBoxLayout()

        search_button = QPushButton('Поиск')
        # search_button.clicked.connect(self.save_text)
        search_button.clicked.connect(self.attempt_search)
        search_button.setFixedSize(60,30)
        button_layout.addWidget(search_button)

        layout.addLayout(button_layout)
        #
        # idk specified anime ig
        #
        label_input_layout_anime = QHBoxLayout()
        label = QLabel("Укажите аниме из списка : ")
        self.anime_name_box = QComboBox()
        self.anime_name_box.setFixedWidth(100)
        self.anime_name_box.addItem("Пока ничего")
        self.anime_name_box.setEnabled(False)
        label_input_layout_anime.addWidget(label)
        label_input_layout_anime.addWidget(self.anime_name_box)
        label_input_layout_anime.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(label_input_layout_anime)
        #
        # find voice button
        #
        button_layout = QHBoxLayout()

        voice_search_button = QPushButton('Найти озвучку')
        # search_button.clicked.connect(self.save_text)
        voice_search_button.clicked.connect(self.search_voices)
        voice_search_button.setFixedSize(120,30)
        button_layout.addWidget(voice_search_button)

        layout.addLayout(button_layout)
        #
        # voice name line
        #
        layout.addSpacerItem(space)
        label_input_layout_voice = QHBoxLayout()

        label = QLabel("Название озвучки :\n\nМожно выбрать несколько")
        self.voice_list_widget = QListWidget()
        self.voice_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.voice_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                
                font-size: 14px;
            }
            QListWidget::item {
                
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

        # self.voice_name_box = QComboBox()
        # self.voice_name_box.setFixedWidth(100)
        
        self.voice_list_widget.addItem("Пока ничего")
        self.voice_list_widget.setEnabled(False)
        label_input_layout_voice.addWidget(label)
        label_input_layout_voice.addWidget(self.voice_list_widget)
        label_input_layout_voice.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(label_input_layout_voice)
        #
        # save button
        #
        
        layout.addSpacerItem(space)
        startup_layout = QHBoxLayout()
        label = QLabel("Автозапуск программы : ")

        self.startup_checkbox = QCheckBox()
        startup_layout.addWidget(label)
        startup_layout.addWidget(self.startup_checkbox)
        startup_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(startup_layout)

        checkbox_layout = QHBoxLayout()
        label = QLabel("Использовать доп. оповещение : ")
        self.notif_checkbox = QCheckBox()
        checkbox_layout.addWidget(label)
        checkbox_layout.addWidget(self.notif_checkbox)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(checkbox_layout)


        button_layout = QHBoxLayout()

        save_button = QPushButton('Сохранить')
        save_button.clicked.connect(self.save_text)
        save_button.setFixedSize(90,30)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        #
        # checkmark
        #

        self.saved_text_display = QLabel('Сохранённые данные появятся здесь')
        self.saved_text_display.setStyleSheet(
            "background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;"
        )
        self.saved_text_display.setWordWrap(True)
        self.saved_text_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.saved_text_display)

        final_button_layout = QHBoxLayout()
        final_button_layout.setSpacing(0)
        self.connect_button = QPushButton("Начать процесс поиска")
        self.connect_button.setFixedSize(200,35)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color : #061c99; /* Blue */
                color : white;
                font-size: 14px;
                margin: 2px -10px;
                font-weight: bold;
                border: 2px solid #dee2e6;
                }
            QPushButton:hover {
                background-color: #0824c4;
                }
            QPushButton:pressed {
                background-color: #0a2cf0;
                }
            QPushButton:disabled {
                background-color: #010621;
                color: #4c4c4d;
                }
        """)
        self.connect_button.clicked.connect(self.start_search)

        self.stop_thread_button = QPushButton("Стоп")
        self.stop_thread_button.setFixedSize(60,35)
        self.stop_thread_button.setStyleSheet("""
            QPushButton {
                background-color : #8f0303; /* Red */
                color : white;
                font-size: 14px;
                font-weight: bold;
                margin: 2px -10px;
                border: 2px solid #dee2e6;
                }
            QPushButton:hover {
                background-color: #bd0404;
                }
            QPushButton:pressed {
                background-color: #f20505;
                }
            QPushButton:disabled {
                background-color: #1f0000;
                color: #4c4c4d;
                }
        """)
        if self.search_bool:
            self.stop_thread_button.setEnabled(True)
            self.start_search_action.setEnabled(False)
        else:
            self.stop_thread_button.setEnabled(False)
            self.start_search_action.setEnabled(True)
        self.stop_thread_button.clicked.connect(self.stop_search)
        final_button_layout.addWidget(self.connect_button)
        final_button_layout.addWidget(self.stop_thread_button)
        layout.addLayout(final_button_layout)

        self.setLayout(layout)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(self.icon_path))
        tray_menu = QMenu()
        self.start_search_action = QAction("Начать поиск", self)
        self.start_search_action.triggered.connect(self.start_search)
        if not self.search_bool:
            self.start_search_action.setEnabled(True)
        else:
            self.start_search_action.setEnabled(False)
        tray_menu.addAction(self.start_search_action)

        self.stop_search_action = QAction("Остановить поиск", tray_menu)
        self.stop_search_action.triggered.connect(self.stop_search)
        tray_menu.addAction(self.stop_search_action)

        
        self.show_action = QAction("Показать окно", tray_menu)
        self.show_action.triggered.connect(lambda: self.show())
        tray_menu.addAction(self.show_action)

        self.hide_action = QAction("Скрыть окно", tray_menu)
        self.hide_action.triggered.connect(lambda: self.hide())
        tray_menu.addAction(self.hide_action)

        self.show_debug_action = QAction("Debug", tray_menu)
        self.show_debug_action.triggered.connect(lambda: self.output_window.show())
        tray_menu.addAction(self.show_debug_action)

        self.quit_action = QAction("Выйти", tray_menu)
        self.quit_action.triggered.connect(lambda: sys.exit(0))
        tray_menu.addSeparator()
        tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.setToolTip("AniNotify")

        self.tray_icon.show()


    async def get_title_list(self,name):
        result = await self.parser.search(title=name)
        titles = [title['title'] for title in result]
        IDs = [id[f'{self.id_type}_id'] for id in result]
        return titles, IDs
    
    async def get_voice_list(self,id):
        info = await self.parser.get_info(id=id, id_type=self.id_type)
        return [i['name'] for i in info['translations']]

    def attempt_search(self):
        self.search_name = self.settings.value('name', '', type=str)
        try:
            self.title_list, self.id_list = asyncio.run(
                self.get_title_list(self.search_name)
            )
        
            self.anime_name_box.clear()
            if self.title_list:
                self.anime_name_box.addItems(self.title_list)
                self.calc_max_text_width(self.anime_name_box)
                self.anime_name_box.setEnabled(True)
            else:
                self.anime_name_box.addItem("Аниме не найдено")
                self.anime_name_box.setEnabled(False)
        except:
            self.display_message()
        # self.voice_name_box.clear()

        # if self.voice_list:
        #     self.voice_name_box.addItems(self.voice_list)
        #     self.voice_name_box.setEnabled(True)
        # else:
        #     self.voice_name_box.addItem('Озвучки не найдены')
        #     self.voice_name_box.setEnabled(False)
    def search_voices(self):
        try:
            self.anime_id = self.id_list[self.title_list.index(self.anime_name_box.currentText())]
        
            self.voice_list = asyncio.run(
                self.get_voice_list(self.anime_id)
            )
            self.voice_list_widget.clear()
            if self.voice_list:
                self.voice_list_widget.addItems(self.voice_list)
                # self.voice_list_widget.setFixedWidth(200)
                self.voice_list_widget.setEnabled(True)
            else:
                self.voice_list_widget.addItem("Озвучки не найдены")
                self.voice_list_widget.setEnabled(False)
        except:
            self.display_message()

    def calc_max_text_width(self, combo_box):
        self.font_metrics = QFontMetrics(combo_box.font())
        max_width = 0
        for i in range(combo_box.count()):
            text = combo_box.itemText(i)
            text_width = self.font_metrics.horizontalAdvance(text)
            max_width = max(max_width, text_width)
        combo_box.setFixedWidth(max_width+30) # offset/padding

    def save_data(self):

        self.settings.setValue('name', self.saved_anime_name)
        self.settings.setValue('voices', self.saved_voices)
        self.settings.setValue('notification', self.saved_notif_bool)
        self.settings.setValue('example', self.search_example)
        self.settings.setValue('id', self.saved_id)
        self.settings.setValue('startup',self.saved_startup_bool)
        self.settings.sync()

    def set_saved_text(self):
        try:
            self.saved_text_display.setText(   
                f"Текущие параметры :\n"
                f"Аниме : {self.saved_anime_name}\n"
                f"Озвучки : {', '.join(self.saved_voices)}\n"
                f"Доп. оповещение : {'Да' if self.saved_notif_bool else 'Нет'}\n"
                f"Автозапуск : {'Да' if self.saved_startup_bool else 'Нет'}")
        except:
            print('error in setting saved text display')
    
    def save_text(self):

        self.saved_id = self.anime_id

        self.saved_anime_name = self.anime_name_box.currentText()

        self.saved_voices = [i.text() for i in self.voice_list_widget.selectedItems()]

        self.saved_startup_bool = self.startup_checkbox.isChecked()

        self.saved_notif_bool = self.notif_checkbox.isChecked()

        self.search_example = None

        if self.saved_startup_bool:
            if self.startup_manager.enable_startup():
                self.display_message(head="Успешно", msg="Автозапуск успешно установлен")
            else:
                self.display_message()
        else:
            if self.startup_manager.disable_startup():
                self.display_message(head="Успешно", msg="Автозапуск успешно удалён")
            else:
                self.display_message()

        self.save_data() 

        self.set_saved_text()

        QMessageBox.information(self, "Успешно", "Данные сохранены")

        print('Saved text')

    def load_data(self):

        self.saved_anime_name = self.settings.value('name', '',type=str)
        self.anime_name_input.setText(self.saved_anime_name)

        self.saved_voices = self.settings.value('voices', '',type=str)
        # for i in range(self.voice_list_widget.count()):
        #     item = self.voice_list_widget.item(i)
        #     if item.text() in self.saved_voices:
        #         item.setSelected(True)
        self.saved_id = self.settings.value('id','',type=str)

        self.saved_notif_bool = self.settings.value('notification',True,type=bool)
        self.notif_checkbox.setChecked(self.saved_notif_bool)
        
        self.saved_startup_bool = self.settings.value('startup',False,type=bool)
        self.startup_checkbox.setChecked(self.saved_startup_bool)

        self.set_saved_text()

    def get_saved_data(self):
        self.saved_keys = self.settings.allKeys()
        data_dict = {}
        for key in self.saved_keys:
            data_dict[key] = self.settings.value(key,'')
        return data_dict
    
    def start_search(self):
        self.search_bool = True
        self.search_started_signal.emit()
        self.hide()
        self.stop_thread_button.setEnabled(True)
        self.connect_button.setEnabled(False)
        self.start_search_action.setEnabled(False)
        self.stop_search_action.setEnabled(True)
        print("Starting search")

    def stop_search(self):
        self.search_bool = False
        print("Attempting stop thread")
        self.stop_search_signal.emit()
        time.sleep(3)
        self.stop_thread_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.start_search_action.setEnabled(True)
        self.stop_search_action.setEnabled(False)


    
    def display_message(self, head="Ошибка", msg='Произошла ошибка!'):
        QMessageBox.information(self, head, msg)

    def change_example(self, example):
        self.settings.setValue('example', example)
        print('changed example')

    def closeEvent(self, event):
        self.save_data()
        event.accept() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec()) 
