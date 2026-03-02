from tkinter import *
from customtkinter import *
from configparser import ConfigParser
from pathlib import Path
from raven_formats.xmlb import compile, decompile
from sys import executable, platform
from tkinterdnd2 import TkinterDnD, DND_FILES
from xmlb_fake import to_fake_xml, from_fake_xml

if platform in ['win64', 'win32']:
    from os import startfile
    fopen = lambda f : startfile(f) #.replace('/','\\')
else: # linux and mac (darwin)
    import subprocess
    fopen = lambda f : subprocess.call(('open' if platform == 'darwin' else 'xdg-open', f))

config_file = Path(executable).parent / 'config.ini' # __file__
config = ConfigParser()
if config_file.exists():
    config.read(config_file)
else:
    config.add_section('CONFIG')
CONFIG = config['CONFIG']

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
        if platform in ['win64', 'win32']:
            self.iconbitmap(Path(__file__).parent / 'MM.ico')
        elif platform == 'darwin':
            self.iconbitmap(Path(__file__).parent / 'MM.icns')
        else: # linux variants
            self.iconphoto(False, PhotoImage(file=Path(__file__).parent / 'MM.png'))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.decompile = True

        self.input_file_name = StringVar()
        self.output_file_name = StringVar()
        self.convert_text = StringVar()
        self.format_string_xmlb = StringVar()
        self.format_string_text = StringVar()
        self.current_theme = StringVar()

        top = CTkFrameDnD(self, corner_radius=0)
        top.pack(fill=X)
        middle = CTkFrameDnD(self, corner_radius=0)
        middle.pack(fill=X)
        bottom = CTkFrame(self, corner_radius=0)
        bottom.pack(fill=X)

        top.drop_target_register(DND_FILES)
        top.dnd_bind('<<Drop>>', self.drop_file)
        #self.dnd_bind('<<DropEnter>>', self.drop_enter)
        #self.dnd_bind('<<DropLeave>>', self.drop_leave)

        middle.drop_target_register(DND_FILES)
        middle.dnd_bind('<<Drop>>', self.drop_output)

        _ = CTkEntry(
            top,
            textvariable=self.input_file_name
        ).pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)
        _ = CTkButton(
            top,
            width=32,
            text='...',
            command=self.pick_file
        ).pack(side=LEFT, padx=(0, 10), pady=10)

        _ = CTkEntry(
            middle,
            textvariable=self.output_file_name
        ).pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)
        _ = CTkButton(
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

        _ = CTkButton(
            bottom,
            textvariable=self.convert_text,
            command=self.convert
        ).pack(side=LEFT, padx=10, pady=10)

        _ = CTkButton(
            bottom,
            text='Edit',
            command=self.edit
        ).pack(side=LEFT, padx=10, pady=10)

        _ = CTkButton(
            bottom,
            text='Save Settings',
            command=self.save_settings
        ).pack(side=LEFT, padx=10, pady=10)

        _ = CTkOptionMenu(
            bottom,
            values=['System', 'Light', 'Dark'],
            variable=self.current_theme,
            command=self.switch_theme
        ).pack(side=RIGHT, padx=10, pady=10)
        _ = CTkLabel(
            bottom,
            text='Change theme:'
        ).pack(side=RIGHT, padx=10, pady=10)

        self.format_string_xmlb.set(CONFIG.get('FORMAT_XMLB', 'engb'))
        self.format_string_text.set(CONFIG.get('FORMAT_TEXT', 'xml'))
        self.current_theme.set(theme := CONFIG.get('THEME', 'System'))
        self.output_file_name.trace_add('write', self.output_file_name_changed)
        self.input_file_name.trace_add('write', self.input_file_name_changed)
        self.input_file_name.set(CONFIG.get('RECENT_INPUT_FILE', ''))
        output_file_name = CONFIG.get('RECENT_OUTPUT_FILE', '')
        if output_file_name:
            self.output_file_name.set(output_file_name)
        if theme != 'System': self.switch_theme(theme)

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
            self.decompile = file.suffix[1:] in XMLB_FORMATS
            if self.decompile:
                self.convert_text.set('Decompile')
                self.format_option_text.pack(side=RIGHT, padx=(0, 10), pady=10)
                self.format_option_xmlb.pack_forget()
                self.output_file_name.set(f'{filename}.{self.format_string_text.get()}')
            else:
                self.convert_text.set('Compile')
                self.format_option_xmlb.pack(side=RIGHT, padx=(0, 10), pady=10)
                self.format_option_text.pack_forget()
                output_path = file.with_name(file.stem)
                if output_path.suffix[1:] not in XMLB_FORMATS:
                    output_path = output_path.with_name(f'{output_path.name}.{self.format_string_xmlb.get()}')
                self.output_file_name.set(output_path)
        else:
            self.convert_text.set('Compile/Decompile')

    def output_file_name_changed(self, *args):
        # https://stackoverflow.com/questions/29690463
        filename = self.output_file_name.get()
        if filename:
            *path, suffix = filename.rsplit('.', 1)
            if path:
                if self.decompile:
                    if suffix not in TEXT_FORMATS:
                        suffix = 'txt'
                    self.format_string_text.set(suffix)
                elif suffix in XMLB_FORMATS:
                        self.format_string_xmlb.set(suffix)

    def switch_format(self, format_string: str):
        output_file_name = self.output_file_name.get()
        if output_file_name:
            output_path = Path(output_file_name)
            self.output_file_name.set(output_path.with_name(f'{output_path.stem}.{format_string}'))

    def switch_theme(self, theme: str):
        set_appearance_mode(theme)

    def convert(self):
        out = self.output_file_name.get()
        inp = self.input_file_name.get()
        if not out or not inp:
            return
        input_path = Path(inp)
        output_path = Path(out)
        if self.decompile:
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
        if self.decompile:
            o = self.output_file_name.get()
            self.output_file_name.set(self.input_file_name.get())
            self.input_file_name.set(o)
            file = Path(o)
        else:
            file = Path(self.input_file_name.get())
        if file.exists():
            fopen(file)

    def save_settings(self):
        config.set('CONFIG', 'FORMAT_XMLB', self.format_string_xmlb.get())
        config.set('CONFIG', 'FORMAT_TEXT', self.format_string_text.get())
        config.set('CONFIG', 'RECENT_INPUT_FILE', self.input_file_name.get())
        config.set('CONFIG', 'RECENT_OUTPUT_FILE', self.output_file_name.get())
        config.set('CONFIG', 'THEME', self.current_theme.get())
        with config_file.open('w') as f:
            config.write(f)

    def on_closing(self):
        self.save_settings()
        self.destroy()

if __name__ == '__main__':
    app = App('Raven-Formats UI')
    app.mainloop()