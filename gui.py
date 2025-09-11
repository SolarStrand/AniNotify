import sys
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QCheckBox, QSpacerItem, QListWidget, QAbstractItemView
)
import asyncio
from anime_parsers_ru import KodikParserAsync

class App(QWidget):
    search_started_signal = pyqtSignal()
    stop_search_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings('Solar','AniNotify')
        self.search_example = self.settings.value('example', None)
        self.parser = KodikParserAsync()
        self.id_type = 'shikimori'
        self.search_bool = False
        self.initUI()
        self.load_data()
        
    def initUI(self):
        self.setWindowTitle("AniNotify")
        self.setGeometry(300,300,500,200)
        self.setMaximumSize(500,200)
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


        button_layout = QHBoxLayout()

        save_button = QPushButton('Сохранить')
        save_button.clicked.connect(self.save_text)
        save_button.setFixedSize(90,30)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        #
        # checkmark
        #

        self.checkbox = QCheckBox("Использовать доп. оповещение (помимо встроенного Windows)")
        layout.addWidget(self.checkbox)

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
        else:
            self.stop_thread_button.setEnabled(False)
        self.stop_thread_button.clicked.connect(self.stop_search)
        final_button_layout.addWidget(self.connect_button)
        final_button_layout.addWidget(self.stop_thread_button)
        layout.addLayout(final_button_layout)

        self.setLayout(layout)

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
        self.settings.setValue('notification', self.checkbox.isChecked())
        self.settings.setValue('example', self.search_example)
        self.settings.setValue('id', self.saved_id)
        self.settings.sync()

    def set_saved_text(self):
        self.saved_text_display.setText(f"""Текущие параметры :\nАниме : {self.saved_anime_name}\nОзвучки : {', '.join(self.saved_voices)}\nДоп. оповещение : {'Да' if self.checkbox.isChecked() else 'Нет'}""")
    def save_text(self):

        self.saved_id = self.anime_id

        self.saved_anime_name = self.anime_name_input.text()

        self.saved_voices = [i.text() for i in self.voice_list_widget.selectedItems()]

        self.search_example = None

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
        
        self.checkbox.setChecked(self.settings.value('notification',True,type=bool))

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
        # self.hide()
        self.stop_thread_button.setEnabled(True)
        self.connect_button.setEnabled(False)
        print("Starting search")

    def stop_search(self):
        self.search_bool = False
        print("Attempting stop thread")
        self.stop_search_signal.emit()
        self.stop_thread_button.setEnabled(False)
        self.connect_button.setEnabled(True)


    
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
