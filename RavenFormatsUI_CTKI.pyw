from tkinter import *
from customtkinter import *
from configparser import ConfigParser
from os import startfile
from pathlib import Path
from raven_formats.xmlb import compile, decompile
from sys import executable
from tkinterdnd2 import TkinterDnD, DND_FILES
from xmlb_fake import to_fake_xml, from_fake_xml
import darkdetect

config_file = Path(executable).parent / 'config.ini' # __file__
config = ConfigParser()
if config_file.exists():
    config.read(config_file) # works with Path?
else:
    config.add_section('CONFIG')
CONFIG = config['CONFIG']
# getfloat()
# getint()
# getboolean()

XMLB_FORMATS = ['engb', 'xmlb', 'itab', 'freb', 'gerb', 'spab', 'rusb', 'polb', 'pkgb', 'boyb', 'chrb', 'navb']
TEXT_FORMATS = ['xml', 'json', 'txt']

set_default_color_theme('green')


class CTkFrameDnD(CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class App(CTk):
    def __init__(self, title):
        super().__init__()
        self.title(title)
        self.iconbitmap(Path(__file__).parent / 'MM.ico')
        # self.geometry(f'{size[0]}x{size[1]}')
        # self.minsize(size[0], size[1])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        #self.instructions = StringVar()
        #
        #self.top = CTkFrame(self, fg_color='transparent')
        #self.top.pack()
        top = CTkFrameDnD(self, corner_radius=0)
        top.pack(fill=X)
        middle = CTkFrameDnD(self, corner_radius=0)
        middle.pack(fill=X)
        bottom = CTkFrame(self, corner_radius=0)
        bottom.pack(fill=X)

        self.input_file_name = StringVar()
        self.output_file_name = StringVar()
        self.convert_text = StringVar()
        self.format_string_xmlb = StringVar()
        self.format_string_text = StringVar()

        top.drop_target_register(DND_FILES)
        top.dnd_bind('<<Drop>>', self.drop_file)
        #self.dnd_bind('<<DropEnter>>', self.drop_enter)
        #self.dnd_bind('<<DropLeave>>', self.drop_leave)

        middle.drop_target_register(DND_FILES)
        middle.dnd_bind('<<Drop>>', self.drop_output)

        input_file_name_e = CTkEntry(
            top,
            textvariable=self.input_file_name
        ).pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)
        browse_button = CTkButton(
            top,
            width=32,
            text='...',
            command=self.pick_file
        ).pack(side=LEFT, padx=(0, 10), pady=10)

        input_file_name_e = CTkEntry(
            middle,
            textvariable=self.output_file_name
        ).pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)
        browse_button = CTkButton(
            middle,
            width=32,
            text='...',
            command=self.pick_output
        ).pack(side=LEFT, padx=(0, 10), pady=10)
        self.format_option_xmlb = CTkOptionMenu(
            middle,
            values=XMLB_FORMATS,
            variable=self.format_string_xmlb,
            command=self.switch_format
        )
        self.format_option_text = CTkOptionMenu(
            middle,
            values=TEXT_FORMATS,
            variable=self.format_string_text,
            command=self.switch_format
        )

        convert_button = CTkButton(
            bottom,
            textvariable=self.convert_text,
            command=self.convert
        ).pack(side=LEFT, padx=10, pady=10)

        edit_button = CTkButton(
            bottom,
            text='Edit',
            command=self.edit
        ).pack(side=LEFT, padx=10, pady=10)

        save_button = CTkButton(
            bottom,
            text='Save Settings',
            command=self.save_settings
        ).pack(side=LEFT, padx=10, pady=10)

        theme_option = CTkOptionMenu(
            bottom,
            values=['System', 'Light', 'Dark'],
            command=self.switch_theme
        ).pack(side=RIGHT, padx=10, pady=10)
        theme_label = CTkLabel(
            bottom,
            text='Change theme:'
        ).pack(side=RIGHT, padx=10, pady=10)

        self.format_string_xmlb.set(CONFIG.get('FORMAT_XMLB', 'engb'))
        self.format_string_text.set(CONFIG.get('FORMAT_TEXT', 'xml'))
        self.output_file_name.trace_add('write', self.output_file_name_changed)
        self.input_file_name.trace_add('write', self.input_file_name_changed)
        self.input_file_name.set(CONFIG.get('RECENT_INPUT_FILE', ''))
        output_file_name = CONFIG.get('RECENT_OUTPUT_FILE', '')
        if output_file_name:
            self.output_file_name.set(output_file_name)

        self.current_theme = 'System'
        self.fix_theme(self.current_theme)

    def drop_file(self, event):
        # if event.data:
        for f in self.tk.splitlist(event.data):
            self.input_file_name.set(f)
            return event.action
        return event.action

    def pick_file(self):
        self.input_file_name.set(filedialog.askopenfilename())

    def drop_output(self, event):
        # if event.data:
        for f in self.tk.splitlist(event.data):
            self.output_file_name.set(f)
            return event.action
        return event.action

    def pick_output(self):
        self.output_file_name.set(filedialog.askopenfilename())

    def input_file_name_changed(self, *args):
        filename = self.input_file_name.get()
        if filename:
            file = Path(filename)
            if file.suffix[1:] in XMLB_FORMATS:
                self.convert_text.set('Decompile')
                self.format_option_text.pack(side=RIGHT, padx=(0, 10), pady=10)
                self.format_option_xmlb.pack_forget()
                self.output_file_name.set(f'{filename}.{self.format_string_text.get()}')
            else:
                self.convert_text.set('Compile')
                self.format_option_xmlb.pack(side=RIGHT, padx=(0, 10), pady=10)
                self.format_option_text.pack_forget()
                output_path = file.with_name(file.stem)
                suffix = output_path.suffix[1:]
                if suffix in XMLB_FORMATS:
                    self.format_string_xmlb.set(suffix)
                else:
                    output_path = output_path.with_name(f'{output_path.name}.{self.format_string_xmlb.get()}')
                self.output_file_name.set(output_path)
        else:
            self.convert_text.set('Compile/Decompile')

    def output_file_name_changed(self, *args):
        # https://stackoverflow.com/questions/29690463
        filename = self.output_file_name.get()
        if filename:
            file = Path(filename)
            suffix = Path(filename).suffix[1:]
            if suffix:
                if suffix in XMLB_FORMATS:
                    self.format_string_xmlb.set(suffix)
                elif suffix in TEXT_FORMATS:
                    self.format_string_text.set(suffix)

    def switch_format(self, format_string: str):
        output_file_name = self.output_file_name.get()
        if output_file_name:
            output_path = Path(output_file_name)
            self.output_file_name.set(output_path.with_name(f'{output_path.stem}.{format_string}'))

    def switch_theme(self, theme: str):
        self.current_theme = theme
        set_appearance_mode(theme)
        self.fix_theme(theme)

    def fix_theme(self, theme: str):
        if theme == 'System': theme = darkdetect.theme()

    def convert(self):
        out = self.output_file_name.get()
        if not out:
            return
        input_path = Path(self.input_file_name.get())
        output_path = Path(out)
        if self.convert_text.get() == 'Decompile':
            if self.format_string_text.get() == 'txt':
                to_fake_xml(input_path, output_path)
            else:
                decompile(input_path, output_path, True)
        else:
            isRF = False
            with input_path.open('r') as f:
                while c := f.read(1):
                    if not c.isspace():
                        isRF = c in ('<', '{') and input_path.suffix in ('.xml', '.json')
                        break
            if isRF:
                compile(input_path, output_path)
            else:
                from_fake_xml(input_path, output_path)

    def edit(self):
        file = Path(self.output_file_name.get())
        if file.exists():
            # from sys import platform
            # if platform == 'darwin':
            #     subprocess.call(('open', filename))
            # elif platform in ['win64', 'win32']:
            startfile(file) #.replace('/','\\')
            # else: # linux variants
            #     subprocess.call(('xdg-open', filename))
            o = self.output_file_name.get()
            self.output_file_name.set(self.input_file_name.get())
            self.input_file_name.set(o)

    def save_settings(self):
        config.set('CONFIG', 'FORMAT_XMLB', self.format_string_xmlb.get())
        config.set('CONFIG', 'FORMAT_TEXT', self.format_string_text.get())
        config.set('CONFIG', 'RECENT_INPUT_FILE', self.input_file_name.get())
        config.set('CONFIG', 'RECENT_OUTPUT_FILE', self.output_file_name.get())
        with config_file.open('w') as f:
            config.write(f)

    def on_closing(self):
        self.save_settings()
        self.destroy()

if __name__ == '__main__':
    app = App('Raven-Formats UI')
    app.mainloop()