from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QComboBox, QLineEdit, 
                             QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from api.ollama_client import OllamaClient
from ui.chat_widgets import ChatArea, ThinkingSection

class ChatWorker(QThread):
    message_received = Signal(str)
    thinking_received = Signal(str)
    error_occurred = Signal(str)
    response_started = Signal()
    
    def __init__(self, client, model, message):
        super().__init__()
        self.client = client
        self.model = model
        self.message = message
    
    def run(self):
        try:
            self.response_started.emit()
            for content_type, content in self.client.chat_stream(self.model, self.message):
                if content_type == 'thinking':
                    self.thinking_received.emit(content)
                elif content_type == 'message':
                    self.message_received.emit(content)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ollama_client = OllamaClient()
        self.conversation_history = []
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        self.setWindowTitle("JGxAAI v1.337")
        self.setWindowIcon(QIcon())
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #000000;")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        header_frame = QFrame()
        header_frame.setFixedHeight(50)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel(">>> JGxAAI TERMINAL <<<")
        title_font = QFont("Courier New", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        
        self.new_chat_button = QPushButton("[NEW CHAT]")
        self.new_chat_button.clicked.connect(self.new_chat)
        self.new_chat_button.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        
        model_label = QLabel("MODEL:")
        model_font = QFont("Courier New", 10, QFont.Weight.Bold)
        model_label.setFont(model_font)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(180)
        self.model_combo.setFont(QFont("Courier New", 10))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.new_chat_button)
        header_layout.addSpacing(10)
        header_layout.addWidget(model_label)
        header_layout.addWidget(self.model_combo)
        
        layout.addWidget(header_frame)
        
        self.chat_area = ChatArea()
        layout.addWidget(self.chat_area)
        
        input_frame = QFrame()
        input_frame.setFixedHeight(60)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("> ENTER COMMAND...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setFont(QFont("Courier New", 12))
        self.message_input.setMinimumHeight(35)
        
        self.send_button = QPushButton("[SEND]")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.send_button.setMinimumSize(70, 35)
        
        input_layout.addWidget(self.message_input)
        input_layout.addSpacing(10)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_frame)
        
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
                color: #00ff00;
            }
            QFrame {
                background: #000000;
                border: none;
                color: #00ff00;
            }
            QLabel {
                color: #00ff00;
                font-weight: bold;
            }
            QLineEdit {
                background: #001100;
                border: 1px solid #00ff00;
                border-radius: 0px;
                padding: 8px;
                color: #00ff00;
                font-size: 12px;
                selection-background-color: #003300;
            }
            QLineEdit:focus {
                border: 2px solid #00ff00;
                background: #002200;
            }
            QPushButton {
                background: #003300;
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 0px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background: #004400;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            QPushButton:pressed {
                background: #002200;
                color: #00aa00;
            }
            QPushButton:disabled {
                background: #001100;
                color: #006600;
                border: 1px solid #006600;
            }
            QComboBox {
                background: #001100;
                border: 1px solid #00ff00;
                border-radius: 0px;
                padding: 5px 8px;
                color: #00ff00;
            }
            QComboBox:hover {
                background: #002200;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #00ff00;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #001100;
                border: 1px solid #00ff00;
                selection-background-color: #003300;
                color: #00ff00;
            }
        """)
    
    def load_models(self):
        try:
            models = self.ollama_client.get_models()
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model['name'])
            if models:
                self.model_combo.setCurrentIndex(0)
        except Exception as e:
            self.chat_area.add_message(f"Error loading models: {str(e)}", is_user=False)
    
    def new_chat(self):
        self.conversation_history = []
        self.chat_area.clear_chat()
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
        
        selected_model = self.model_combo.currentText()
        if not selected_model:
            self.chat_area.add_message("No model selected", is_user=False)
            return
        
        self.message_input.clear()
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        
        self.chat_area.add_message(message, is_user=True)
        
        self.conversation_history.append({"role": "user", "content": message})
        
        self.current_response = ""
        self.current_thinking = None
        self.full_thinking_content = ""
        
        self.worker = ChatWorker(self.ollama_client, selected_model, self.conversation_history)
        self.worker.message_received.connect(self.on_message_received)
        self.worker.thinking_received.connect(self.on_thinking_received)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.response_started.connect(self.on_response_started)
        self.worker.finished.connect(self.on_chat_finished)
        self.worker.start()
    
    def on_response_started(self):
        pass
    
    def on_thinking_received(self, full_thinking):
        self.full_thinking_content = full_thinking
    
    def on_message_received(self, chunk):
        self.current_response += chunk
    
    def on_error(self, error_msg):
        self.chat_area.add_message(f"Error: {error_msg}", is_user=False)
    
    def on_chat_finished(self):
        if self.current_response.strip():
            self.chat_area.add_message(self.current_response, is_user=False)
            self.conversation_history.append({"role": "assistant", "content": self.current_response})
        
        if self.full_thinking_content.strip():
            thinking_section = self.chat_area.add_thinking_section()
            thinking_section.set_thinking_content(self.full_thinking_content)
        
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()