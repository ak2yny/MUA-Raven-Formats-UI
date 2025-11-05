from itertools import chain
from pathlib import Path
from raven_formats.xmlb import read_xmlb, write_xmlb
import xml.etree.ElementTree as ET

def from_fake_xml_element(lines: list, index: int = 0) -> tuple[ET.Element, int]:
    element = ET.Element(lines[index][:-1].strip())
    index += 1
    while (line := lines[index].strip()) != '}':
        if line:
            if line[-1] == '{':
                sub_element, index = from_fake_xml_element(lines, index)
                element.append(sub_element)
            elif '=' in line:
                name, value = line.split('=', 1)
                element.set(name.strip(), value.rstrip(' ;').strip())
            #else: raise ValueError('')
        index += 1

    return element, index

def to_fake_xml_element(element: ET.Element, indent: int, ni: int = 0) -> list:
    i = ' ' * ni
    #for sub_element in element:
    #    lines_output.extend(to_fake_xml_element(sub_element, indent, ni + indent))
    return f'{i}{element.tag} {{\n' + \
           '\n'.join(chain(
            (f'{i}{name} = {value} ;' for name, value in element.items()),
            (to_fake_xml_element(sub_element, indent, ni + indent) for sub_element in element)
           )) + \
           f'\n{i}}}\n'

def from_fake_xml(input_path: Path, output_path: Path):
    root_element, _ = from_fake_xml_element(input_path.read_text().lstrip().lstrip('XMLB ').split('\n'))
    write_xmlb(root_element, output_path)

def to_fake_xml(input_path: Path, output_path: Path, indent: int = 3):
    output_path.write_text('XMLB ' + to_fake_xml_element(read_xmlb(input_path), indent))
