from PyQt6.QtWidgets import (QApplication, QMainWindow, QCheckBox, 
                             QVBoxLayout, QWidget, QLabel, QPushButton, QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QIcon, QAction


app = QApplication([])
app.setQuitOnLastWindowClosed(False)
icon = QIcon('aninotify_icon.png')
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)
menu = QMenu()
quit_action = QAction("Quit")
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)
tray.setContextMenu(menu)
app.exec()