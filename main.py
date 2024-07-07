import sys
import json
import spacy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTextEdit, QFileDialog, QListWidget, QListWidgetItem,
    QLineEdit, QLabel, QMenu, QAction, QStatusBar
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QBrush, QColor, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QSizePolicy

class CustomListItem(QWidget):
    def __init__(self, text, color):
        super().__init__()
        layout = QHBoxLayout()

        brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
        text_color = 'black' if brightness > 128 else 'white'

        label = QLabel(text)
        label.setStyleSheet(f"background-color: {color.name()}; color: {text_color}; border-radius: 10px; padding: 5px;")
        layout.addWidget(label)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)



class NERTagger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.nlp = spacy.load("en_core_web_sm")
        self.tagged_words = []
        self.undo_stack = []
        self.redo_stack = []
        self.tag_colors = {}

    def initUI(self):
        self.setWindowTitle('SpaCy NER Fine-tuning Tool')
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        self.font = QFont()
        self.font.setPointSize(14)

        # Create a vertical layout to hold the label and text edit
        left_v_layout = QVBoxLayout()
        left_v_layout.setContentsMargins(0, 0, 0, 0)
        left_v_layout.setSpacing(10)

        self.text_edit_label = QLabel("Highlight word(s) and tag", self)
        self.text_edit_label.setAlignment(Qt.AlignCenter)
        self.text_edit_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_v_layout.addWidget(self.text_edit_label)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(self.font)
        self.text_edit.setStyleSheet("background-color: #1E1E1E; color: white;")
        left_v_layout.addWidget(self.text_edit)

        self.layout.addLayout(left_v_layout, 0, 0, 1, 6)

        # Create a vertical layout to hold the tagged list label and the tagged list
        right_v_layout = QVBoxLayout()
        right_v_layout.setContentsMargins(0, 0, 0, 0)
        right_v_layout.setSpacing(10)

        self.tagged_list_label = QLabel("List of Tagged entities", self)
        self.tagged_list_label.setAlignment(Qt.AlignCenter)
        self.tagged_list_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_v_layout.addWidget(self.tagged_list_label)

        self.tagged_list = QListWidget(self)
        self.tagged_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tagged_list.customContextMenuRequested.connect(self.show_list_context_menu)
        self.tagged_list.setFont(self.font)
        self.tagged_list.setStyleSheet("background-color: #1E1E1E; color: white;")
        right_v_layout.addWidget(self.tagged_list)

        self.layout.addLayout(right_v_layout, 0, 6, 1, 4)

        # Add buttons and input fields
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.open_button = QPushButton('Open File', self)
        self.open_button.clicked.connect(self.open_file)
        self.open_button.setStyleSheet("background-color: #3A3A3A; color: white;padding:10px;font-weight:500")
        button_layout.addWidget(self.open_button)

        self.save_button = QPushButton('Save to JSON', self)
        self.save_button.clicked.connect(self.save_to_json)
        self.save_button.setStyleSheet("background-color: #238636;font-weight:500; color: white;padding:10px")
        button_layout.addWidget(self.save_button)

        self.tag_input = QLineEdit(self)
        self.tag_input.setPlaceholderText('Enter tag here...')
        self.tag_input.returnPressed.connect(self.tag_selected_text)
        self.tag_input.setStyleSheet("background-color: #1E1E1E; color: white;")
        button_layout.addWidget(self.tag_input)

        self.layout.addLayout(button_layout, 1, 0, 1, 10)

        # Create a vertical layout for bulk tagging
        bulk_v_layout = QVBoxLayout()
        bulk_v_layout.setContentsMargins(0, 10, 0, 0)

        self.bulk_label = QLabel("Bulk Tagging:", self)
        bulk_v_layout.addWidget(self.bulk_label)

        self.bulk_input = QLineEdit(self)
        self.bulk_input.setPlaceholderText('Enter text to tag...')
        self.bulk_input.setStyleSheet("background-color: #1E1E1E; color: white;")
        bulk_v_layout.addWidget(self.bulk_input)

        self.bulk_tag_input = QLineEdit(self)
        self.bulk_tag_input.setPlaceholderText('Enter tag for bulk text...')
        self.bulk_tag_input.setStyleSheet("background-color: #1E1E1E; color: white;")
        bulk_v_layout.addWidget(self.bulk_tag_input)

        self.bulk_tag_button = QPushButton('Apply Bulk Tag', self)
        self.bulk_tag_button.clicked.connect(self.apply_bulk_tag)
        self.bulk_tag_button.setStyleSheet("background-color: #3A3A3A; color: white;font-weight:500")
        bulk_v_layout.addWidget(self.bulk_tag_button)

        # Add the vertical layout to the main layout
        self.layout.addLayout(bulk_v_layout, 2, 0, 1, 10)

        # Add undo and redo actions
        self.undo_action = QAction('Undo', self)
        self.undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        self.undo_action.triggered.connect(self.undo)

        self.redo_action = QAction('Redo', self)
        self.redo_action.setShortcut(QKeySequence('Ctrl+Y'))
        self.redo_action.triggered.connect(self.redo)

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

        self.text_edit.cursorPositionChanged.connect(self.focus_tag_input)

        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add credits
        self.credits = QLabel('<a href="https://github.com/MaddyDev-Glitch" style="color: white; text-decoration: none;">Developed by MaddyDev-Glitch ✨</a>', self)
        self.credits.setOpenExternalLinks(True)
        self.credits.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        self.layout.addWidget(self.credits, 3, 0, 1, 10)

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                text = file.read()
                self.display_sentences(text)

    def display_sentences(self, text):
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        self.text_edit.setPlainText("\n".join(sentences))

    def focus_tag_input(self):
        if self.text_edit.textCursor().selectedText():
            self.tag_input.setFocus()

    def apply_bulk_tag(self):
        text_to_tag = self.bulk_input.text().strip()
        tag = self.bulk_tag_input.text().strip().upper()
        if text_to_tag and tag:
            doc = self.text_edit.toPlainText()
            cursor = self.text_edit.textCursor()
            start_pos = 0
            while start_pos != -1:
                start_pos = doc.find(text_to_tag, start_pos)
                if start_pos != -1:
                    end_pos = start_pos + len(text_to_tag)
                    cursor.setPosition(start_pos)
                    cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
                    sentence_start = self.text_edit.toPlainText().rfind("\n", 0, start_pos) + 1
                    sentence_end = self.text_edit.toPlainText().find("\n", end_pos)
                    if sentence_end == -1:
                        sentence_end = len(self.text_edit.toPlainText())
                    sentence = self.text_edit.toPlainText()[sentence_start:sentence_end].strip()
                    word_start = start_pos - sentence_start
                    word_end = end_pos - sentence_start

                    annotation = {
                        'id': len(self.tagged_words) + 1,
                        'sentence': sentence,
                        'annotation': {
                            'word': text_to_tag,
                            'start': word_start,
                            'end': word_end,
                            'tag_name': tag
                        }
                    }
                    if not self.is_duplicate(annotation):
                        self.tagged_words.append(annotation)
                        self.undo_stack.append(('add', annotation))
                        self.redo_stack.clear()
                        self.highlight_text(start_pos, end_pos, self.get_tag_color(tag))
                    start_pos += len(text_to_tag)
            self.update_tagged_list()

    def tag_selected_text(self):
        selected_text = self.text_edit.textCursor().selectedText()
        tag = self.tag_input.text().strip().upper()
        cursor = self.text_edit.textCursor()
        if selected_text and tag:
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            sentence_start = self.text_edit.toPlainText().rfind("\n", 0, start_pos) + 1
            sentence_end = self.text_edit.toPlainText().find("\n", end_pos)
            if sentence_end == -1:
                sentence_end = len(self.text_edit.toPlainText())
            sentence = self.text_edit.toPlainText()[sentence_start:sentence_end].strip()
            word_start = start_pos - sentence_start
            word_end = end_pos - sentence_start

            annotation = {
                'id': len(self.tagged_words) + 1,
                'sentence': sentence,
                'annotation': {
                    'word': selected_text,
                    'start': word_start,
                    'end': word_end,
                    'tag_name': tag
                }
            }
            if not self.is_duplicate(annotation):
                self.tagged_words.append(annotation)
                self.undo_stack.append(('add', annotation))
                self.redo_stack.clear()

                self.update_tagged_list()
                self.highlight_text(start_pos, end_pos, self.get_tag_color(tag))

                self.tag_input.clear()

    def is_duplicate(self, annotation):
        for item in self.tagged_words:
            if (item['sentence'] == annotation['sentence'] and
                item['annotation']['word'] == annotation['annotation']['word'] and
                item['annotation']['start'] == annotation['annotation']['start'] and
                item['annotation']['end'] == annotation['annotation']['end'] and
                item['annotation']['tag_name'] == annotation['annotation']['tag_name']):
                return True
        return False

    def get_tag_color(self, tag):
        if tag not in self.tag_colors:
            self.tag_colors[tag] = QColor.fromHsv(len(self.tag_colors) * 30 % 360, 255, 255)
        return self.tag_colors[tag]

    def update_tagged_list(self):
        self.tagged_list.clear()
        for item in self.tagged_words:
            sentence_preview = (item['sentence'][:10] + '...') if len(item['sentence']) > 10 else item['sentence']
            display_text = f"{sentence_preview} - {item['annotation']['word']} ({item['annotation']['tag_name']})"
            list_item = QListWidgetItem()
            list_item_widget = CustomListItem(display_text, self.get_tag_color(item['annotation']['tag_name']))
            list_item.setSizeHint(list_item_widget.sizeHint())
            self.tagged_list.addItem(list_item)
            self.tagged_list.setItemWidget(list_item, list_item_widget)
            list_item.setData(Qt.UserRole, item)

    def delete_tagged_item(self, item):
        self.tagged_words.remove(item)
        self.undo_stack.append(('delete', item))
        self.redo_stack.clear()
        self.update_tagged_list()
        self.clear_highlights()
        self.rehighlight_all()

    def save_to_json(self):
        json_data = {
            'examples': [
                {
                    'id': str(item['id']),
                    'content': item['sentence'],
                    'annotation': [
                        {
                            'word': item['annotation']['word'],
                            'start': item['annotation']['start'],
                            'end': item['annotation']['end'],
                            'tag_name': item['annotation']['tag_name']
                        }
                    ]
                } for item in self.tagged_words
            ]
        }
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
                self.status_bar.showMessage(f"Data saved to {file_name}", 5000)

    def show_list_context_menu(self, pos):
        item = self.tagged_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(lambda: self.delete_tagged_item(item.data(Qt.UserRole)))
            menu.addAction(delete_action)
            menu.exec_(self.tagged_list.mapToGlobal(pos))

    def highlight_text(self, start, end, color):
        cursor = self.text_edit.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        char_format = QTextCharFormat()
        char_format.setBackground(QBrush(color))
        cursor.setCharFormat(char_format)

    def clear_highlights(self):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        char_format = QTextCharFormat()
        char_format.setBackground(QBrush(Qt.transparent))
        cursor.setCharFormat(char_format)

    def rehighlight_all(self):
        for item in self.tagged_words:
            sentence_start = self.text_edit.toPlainText().find(item['sentence'])
            if sentence_start != -1:
                start = sentence_start + item['annotation']['start']
                end = sentence_start + item['annotation']['end']
                self.highlight_text(start, end, self.get_tag_color(item['annotation']['tag_name']))

    def undo(self):
        if self.undo_stack:
            action, item = self.undo_stack.pop()
            if action == 'add':
                self.tagged_words.remove(item)
                self.redo_stack.append(('add', item))
            elif action == 'delete':
                self.tagged_words.append(item)
                self.redo_stack.append(('delete', item))
            self.update_tagged_list()
            self.clear_highlights()
            self.rehighlight_all()

    def redo(self):
        if self.redo_stack:
            action, item = self.redo_stack.pop()
            if action == 'add':
                self.tagged_words.append(item)
                self.undo_stack.append(('add', item))
            elif action == 'delete':
                self.tagged_words.remove(item)
                self.undo_stack.append(('delete', item))
            self.update_tagged_list()
            self.clear_highlights()
            self.rehighlight_all()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NERTagger()
    window.show()
    sys.exit(app.exec_())
