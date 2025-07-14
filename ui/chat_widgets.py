from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QTextEdit, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor

class MessageBubble(QLabel):
    def __init__(self, message, is_user=True, parent=None):
        self.is_user = is_user
        
        # Add prefix for user/assistant
        prefix = "[USER]" if self.is_user else "[ASSISTANT]"
        full_message = f"{prefix} {message}"
        
        super().__init__(full_message, parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        font = QFont("Courier New", 12)
        self.setFont(font)
        
        if self.is_user:
            self.setStyleSheet("""
                QLabel {
                    background: #001100;
                    border: 1px solid #00ff00;
                    border-radius: 3px;
                    padding: 8px 12px;
                    color: #00ff00;
                    max-width: 500px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background: #001a00;
                    border: 1px solid #00aa00;
                    border-radius: 3px;
                    padding: 8px 12px;
                    color: #00cc00;
                    max-width: 500px;
                }
            """)

class ThinkingSection(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        self.thinking_content = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        self.toggle_button = QPushButton("[SHOW REASONING]")
        self.toggle_button.clicked.connect(self.toggle_expanded)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background: #003300;
                color: #ffff00;
                border: 1px solid #ffff00;
                border-radius: 0px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
                font-family: "Courier New";
            }
            QPushButton:hover {
                background: #004400;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            QPushButton:pressed {
                background: #002200;
            }
        """)
        
        self.content_area = QTextEdit()
        self.content_area.setVisible(False)
        self.content_area.setReadOnly(True)
        self.content_area.setMaximumHeight(200)
        self.content_area.setStyleSheet("""
            QTextEdit {
                background: #001a1a;
                border: 1px solid #006666;
                border-radius: 0px;
                padding: 8px;
                font-size: 10px;
                color: #00aaaa;
                font-family: "Courier New";
            }
            QScrollBar:vertical {
                background: #001a1a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #006666;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        
        self.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        # Set size policy to fit content
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        
    def add_thinking_content(self, content):
        self.thinking_content += content
        self.content_area.setPlainText(self.thinking_content)
        
        cursor = self.content_area.textCursor()
        cursor.moveToEnd()
        self.content_area.setTextCursor(cursor)
        
    def set_thinking_content(self, content):
        self.thinking_content = content
        self.content_area.setPlainText(content)
        
        if content.strip():
            self.toggle_button.setText("[SHOW REASONING]")
            self.toggle_button.setVisible(True)
        else:
            self.toggle_button.setVisible(False)
        
    def toggle_expanded(self):
        self.is_expanded = not self.is_expanded
        self.content_area.setVisible(self.is_expanded)
        
        if self.is_expanded:
            self.toggle_button.setText("[HIDE REASONING]")
        else:
            self.toggle_button.setText("[SHOW REASONING]")

class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("background: #000000;")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        self.setWidget(self.chat_widget)
        
        self.setStyleSheet("""
            QScrollArea {
                background: #000000;
                border: none;
            }
            QScrollBar:vertical {
                background: #001100;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #00aa00;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00ff00;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
    def add_message(self, message, is_user=True):
        bubble = MessageBubble(message, is_user)
        
        # Create container for alignment
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
            container_layout.addSpacing(10)
        else:
            container_layout.addSpacing(10)
            container_layout.addWidget(bubble)
            container_layout.addStretch()
            
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        self.scroll_to_bottom()
        
    def add_thinking_section(self):
        self.current_thinking = ThinkingSection()
        
        # Create container for alignment (same as assistant messages)
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        container_layout.addSpacing(10)
        container_layout.addWidget(self.current_thinking)
        container_layout.addStretch()
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        self.scroll_to_bottom()
        return self.current_thinking
        
    def scroll_to_bottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def clear_chat(self):
        # Remove all widgets except the stretch
        for i in reversed(range(self.chat_layout.count() - 1)):
            item = self.chat_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)