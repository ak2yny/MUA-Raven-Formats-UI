# Raven-Formats UI

Graphic User Interface for [Raven-Formats](https://github.com/nikita488/raven-formats )' Xmlb by @nikita488. Successor of XMLBCUI for modding compiled XML files in XML and MUA games by Raven Software.


### Download

[Latest version](https://github.com/ak2yny/MUA-Raven-Formats-UI/releases/latest)

This app is portable and shouldn't require anything, except Windows.


### Instructions

You can drag & drop, browse, type or paste input and output files. The output file is automatically chosen, but can be manually changed the same way as the input file. Click on "Compile" or "Decompile" to convert the input to the output. Click on "Edit" do edit the decompiled file (if just decompiled, the app automatically switches to compile mode).

There are additional options to select extension and decompile formats with a drop-down, as well as manually selecting the dark/light theme.

The last used files are saved to a config.ini, which would be very convenient for those who only use it to edit the herostat.


### Build Instructions

Requirements:
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) !

Following requirements are automatically installed:
- [Custom TkInter](https://github.com/TomSchimansky/CustomTkinter)
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)
- [Raven-Formats](https://github.com/nikita488/raven-formats)

To build, simply run [build.bat](https://github.com/ak2yny/MUA-Raven-Formats-UI/blob/master/build.bat).
