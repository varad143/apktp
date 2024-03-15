from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard
from kivy.uix.slider import Slider
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import sqlite3
from datetime import datetime

def encrypt_string(input_string, shift=3):
    encrypted_string = ""
    for char in input_string:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            encrypted_string += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            encrypted_string += char
    return encrypted_string

def decrypt_string(encrypted_string, shift=3):
    decrypted_string = ""
    for char in encrypted_string:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            decrypted_string += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
        else:
            decrypted_string += char
    return decrypted_string

class SecretCodeGenerator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [30]
        self.spacing = 50
        self.current_frame = None
        self.conn = sqlite3.connect('messages.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                             (encrypted_text TEXT, shift INTEGER, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CODES
                             (encrypted_text TEXT, shift INTEGER, timestamp TEXT)''')
        self.create_logo_frame()

    def encrypt_page(self, instance):
        self.clear_widgets()

        label_input = Label(text="Enter a String To Encrypt :", font_size='20sp', size_hint_y=None, height=50)
        self.add_widget(label_input)

        self.input_entry = TextInput(font_size='16sp', size_hint_y=None, height=50)
        self.add_widget(self.input_entry)

        label_shift = Label(text="Select the code : ", font_size='20sp', size_hint_y=None, height=50)
        self.add_widget(label_shift)

        self.shift_slider = Slider(min=1, max=26, value=3)
        self.add_widget(self.shift_slider)

        self.shift_label = Label(text=f"Shift Value: {int(self.shift_slider.value)}", font_size='16sp')
        self.add_widget(self.shift_label)

        self.shift_slider.bind(on_touch_move=self.update_shift_label)

        self.decrypted_label = Label(text="", font_size='16sp')
        self.add_widget(self.decrypted_label)

        # self.encrypted_label = Label(text="Encrypted String:", font_size='20sp')
       # self.add_widget(self.encrypted_label)  # Add label for encrypted string

        button_encrypt = Button(text="Encrypt", font_size='20sp', size_hint_y=None, height=50)
        button_encrypt.bind(on_press=self.encrypt_input_callback)
        self.add_widget(button_encrypt)

        button_copy = Button(text="Copy", font_size='20sp', size_hint_y=None, height=50)
        button_copy.bind(on_press=self.copy_input)
        self.add_widget(button_copy)

        button_back = Button(text="<--", font_size='20sp', size_hint_y=None, height=50)
        button_back.bind(on_press=self.create_home_frame)
        self.add_widget(button_back)

        # Bind on_text event of TextInput to update_encrypted_label method
        self.input_entry.bind(on_text=self.update_encrypted_label)

    def update_encrypted_label(self, instance, value):
        input_string = self.input_entry.text
        shift_value = int(self.shift_slider.value)
        encrypted_string = encrypt_string(input_string, shift_value)
        self.encrypted_label.text = f"Encrypted String: \n{input_string}"

    def decrypt_page(self, instance):
        self.clear_widgets()

        label_input = Label(text="Enter a String To Decrypt :", font_size='20sp', size_hint_y=None, height=50)
        self.add_widget(label_input)

        self.input_entry = TextInput(font_size='16sp', size_hint_y=None, height=50)
        self.add_widget(self.input_entry)

        label_shift = Label(text=f"Select the code : ", font_size='20sp', size_hint_y=None, height=50)
        self.add_widget(label_shift)

        self.shift_slider = Slider(min=1, max=26, value=3)
        self.add_widget(self.shift_slider)

        self.shift_label = Label(text=f"Shift Value: {int(self.shift_slider.value)}", font_size='16sp')
        self.add_widget(self.shift_label)

        self.shift_slider.bind(on_touch_move=self.update_shift_label)

        self.decrypted_label = Label(text="", font_size='16sp')
        self.add_widget(self.decrypted_label)

        button_decrypt = Button(text="Decrypt", font_size='20sp', size_hint_y=None, height=50)
        button_decrypt.bind(on_press=self.decrypt_input_callback)
        self.add_widget(button_decrypt)

        button_copy = Button(text="Copy", font_size='20sp', size_hint_y=None, height=50)
        button_copy.bind(on_press=self.copy_input)
        self.add_widget(button_copy)

        button_back = Button(text="<--", font_size='20sp', size_hint_y=None, height=50)
        button_back.bind(on_press=self.create_home_frame)  # Corrected here
        self.add_widget(button_back)

    def copy_input(self, instance):
        input_string = self.input_entry.text
        shift_value = int(self.shift_slider.value)
        copied_string = encrypt_string(input_string, shift_value)
        Clipboard.copy(copied_string)

    def encrypt_input_callback(self, instance):
        # Check if the label already exists and clear the widgets
        if hasattr(self, 'encrypted_label'):
            self.remove_widget(self.encrypted_label)

        input_string = self.input_entry.text
        shift_value = int(self.shift_slider.value)
        encrypted_string = encrypt_string(input_string, shift_value)
        if len(encrypted_string) > 100:
            encrypted_string = '\n'.join([encrypted_string[i:i + 100] for i in range(0, len(encrypted_string), 100)])
        # Create the encrypted label and update its text
        self.encrypted_label = Label(text="Encrypted String: " + encrypted_string)
        self.add_widget(self.encrypted_label)  # Add the label to the layout
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO messages VALUES (?,?,?)",
                            (encrypted_string, shift_value, timestamp))
        self.cursor.execute("INSERT INTO CODES VALUES (?,?,?)",
                            (encrypted_string, shift_value, timestamp))  # Save to CODES table
        self.conn.commit()

    def decrypt_input_callback(self, instance):
        input_string = self.input_entry.text
        shift_value = int(self.shift_slider.value)
        decrypted_string = decrypt_string(input_string, shift_value)
        if len(decrypted_string) > 100:
            decrypted_string = '\n'.join([decrypted_string[i:i + 100] for i in range(0, len(decrypted_string), 100)])
        self.decrypted_label.text = decrypted_string

    def create_logo_frame(self):
        self.clear_widgets()

        label_logo = Label(text="Tap here to continue", font_size='20sp', size_hint_y=None, height=50)
        button_logo = Button(text="Tap here to continue", font_size='20sp', size_hint_y=None, height=50)
        button_logo.bind(on_press=self.create_home_frame)

        self.add_widget(label_logo)
        self.add_widget(button_logo)

    def create_home_frame(self, instance):
        self.clear_widgets()

        label_home = Label(text="Welcome to Vsec", font_size='30sp', size_hint_y=None, height=50)
        self.add_widget(label_home)

        button_code = Button(text="Encrypt Code", font_size='20sp', size_hint_y=None, height=50)
        button_code.bind(on_press=self.encrypt_page)
        self.add_widget(button_code)

        button_dcode = Button(text="Decrypt Code", font_size='20sp', size_hint_y=None, height=50)
        button_dcode.bind(on_press=self.decrypt_page)
        self.add_widget(button_dcode)

        button_history = Button(text="History", font_size='20sp', size_hint_y=None, height=50)
        button_history.bind(on_press=self.history_page)  # Bind to history page
        self.add_widget(button_history)


        button_quit = Button(text="Quit Code", font_size='20sp', size_hint_y=None, height=50)
        button_quit.bind(on_press=self.quit_app)
        self.add_widget(button_quit)

    def quit_app(self, instance):
        App.get_running_app().stop()

    def update_shift_label(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.shift_label.text = f"Shift Value: {int(instance.value)}"

    def history_page(self, instance):
        self.clear_widgets()
        self.cursor.execute("SELECT * FROM CODES")
        rows = self.cursor.fetchall()

        if rows:
            layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))

            for row in rows:
                encrypted_string, shift_value, timestamp = row
                label_encrypted = Label(text=encrypted_string, font_size='16sp')
                label_shift = Label(text=str(shift_value), font_size='16sp')
                label_timestamp = Label(text=timestamp, font_size='16sp')

                layout.add_widget(label_encrypted)
                layout.add_widget(label_shift)
                layout.add_widget(label_timestamp)

            scrollview = ScrollView()
            scrollview.add_widget(layout)
            self.add_widget(scrollview)
        else:
            label_no_history = Label(text="No history available", font_size='16sp')
            self.add_widget(label_no_history)

        button_back = Button(text="Back", font_size='20sp', size_hint_y=None, height=50)
        button_back.bind(on_press=self.create_home_frame)
        self.add_widget(button_back)

class SecretCodeGeneratorApp(App):
    def build(self):
        return SecretCodeGenerator()

if __name__ == '__main__':
    SecretCodeGeneratorApp().run()
