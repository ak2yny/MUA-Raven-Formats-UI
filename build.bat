set install_requirements=pip install -r script.requirements.txt
set arguments=--specpath dist --onefile --version-file=..\script.txt --icon=..\MM.ico script.pyw  --add-data "..\MM.ico;." --add-data "..\xmlb_fake.py;." --additional-hooks-dir=.


REM pip install pyinstaller
REM if not errorlevel 0 exit
REM %install_requirements:script=RavenFormatsUI%
REM pyinstaller %arguments:script=RavenFormatsUI% --add-data "..\tkBreeze;tkBreeze"


REM ----------------- CustomTkInter Variant --------------------

%install_requirements:script=RavenFormatsUI_CTKI%
if not errorlevel 0 exit
python build.py

REM set arguments=%arguments:onefile=onedir%
REM pyinstaller %arguments:script=RavenFormatsUI_CTKI% --noconfirm --windowed --add-data "%l:\=/%/customtkinter;customtkinter/"
