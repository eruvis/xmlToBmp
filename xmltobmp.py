from pathlib import Path
from xml.etree import cElementTree as ElementTree
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager

isShowDegubLine = False


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})


def getFontStyle(code):
    cursive = 'normal'
    weight = 'normal'
    # underline = False
    if code in [1, 3, 5, 7]:
        weight = 'bold'
    if code in [2, 3, 6, 7]:
        cursive = 'italic'
    # if code in [4, 5, 6, 7]:
    #     underline = True
    return cursive, weight


def getFontPath(font_name, style, weight):
    if font_name == '': font_name = 'Helvetica'  # default draw.io font
    if style == 'normal' and font_name == 'Helvetica' and weight == 'bold':
        return str(Path.home()) + '\AppData\Local\Microsoft\Windows\Fonts\helvetica_bold.otf'  # FontProperties не находит helvetica bold, пришлось сделать так

    font = font_manager.FontProperties(family=font_name, style=style, weight=weight)
    file = font_manager.findfont(font)
    return file


# while text_width > textbox_width and font_size != 1:
#     font_size -= 1
#     font = ImageFont.truetype(font_path, size=font_size)
#     text_width = idraw.textlength(text, font=font)


def getFormattedFontSizeByWords(idraw, text, font_path, font_size, textbox_width):
    words = text.split()

    for word in words:
        font = ImageFont.truetype(font_path, size=font_size)
        word_width = idraw.textlength(word, font=font)

        while word_width > textbox_width:
            font_size -= 1
            font = ImageFont.truetype(font_path, size=font_size)
            word_width = idraw.textlength(word, font=font)

    return font_size


def getFormattedTextAndFont(idraw, text, font_path, font_size, textbox_width, textbox_height, text_coordinates, text_anchor):
    flag = True

    while flag:
        formatted_text = ''
        temp_text = text
        font = ImageFont.truetype(font_path, size=font_size)
        text_width = idraw.textlength(temp_text, font=font)  #
        symbol_weight = text_width / len(temp_text)  #
        max_symbols_in_line = int(textbox_width / symbol_weight)  #

        while text_width > textbox_width:
            temp_line = temp_text[:max_symbols_in_line]
            space_index = temp_line.rfind(' ')
            # print('TEMP LINE:', temp_line)

            if space_index == -1:
                print('break')
                break

            if formatted_text != '': formatted_text += '\n'
            formatted_text += temp_text[:space_index]
            # print('FORMATED TEXT:', formatted_text)

            temp_text = temp_text[space_index + 1:]
            # print('TEXT:', text)
            text_width = idraw.textlength(temp_text, font=font)
            # print('textwidth:', text_width, 'boxwidth:', textbox_width, '\n')

        if formatted_text != '':
            formatted_text += '\n' + temp_text
        else:
            formatted_text = temp_text

        bbox = idraw.textbbox(text_coordinates, formatted_text, font=font, anchor=text_anchor)
        text_height = bbox[3] - bbox[1]
        # print(text_height, textbox_height)
        if text_height > textbox_height:
            font_size -= 1
        else:
            flag = False

    return formatted_text, ImageFont.truetype(font_path, size=font_size)


def getFormattedText1(text, idraw, font, textbox_width):
    formatted_text = ''

    text_width = idraw.textlength(text, font=font)  #
    symbol_weight = text_width / len(text)  #
    max_symbols_in_line = int(textbox_width / symbol_weight)  #

    while text_width > textbox_width:
        temp_line = text[:max_symbols_in_line]
        space_index = temp_line.rfind(' ')

        if space_index == -1:
            break

        if formatted_text != '': formatted_text += '\n'
        formatted_text += text[:space_index]

        text = text[space_index + 1:]
        text_width = idraw.textlength(text, font=font)

    formatted_text += '\n' + text[:space_index]

    return formatted_text


def createImage(size, color):
    return Image.new('RGB', (size[2], size[3]), color)


def drawFigure(idraw, size, color):
    if color == '':
        idraw.rectangle(size)
    else:
        idraw.rectangle(size, color)


# def checkHeightText():

def getFormattedFontByWidth(idraw, text, text_width, textbox_width, font_size, font_path):
    font = ImageFont.truetype(font_path, size=font_size)
    while text_width > textbox_width and font_size != 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, size=font_size)
        text_width = idraw.textlength(text, font=font)
    return font


def getFormattedFontByHeight(idraw, text, textbox_height, font_size, font_path, text_coordinates, font, text_anchor):
    bbox = idraw.textbbox(text_coordinates, text, font=font, anchor=text_anchor)
    text_height = bbox[3] - bbox[1]
    while text_height > textbox_height:
        font_size -= 1
        font = ImageFont.truetype(font_path, size=font_size)

        bbox = idraw.textbbox(text_coordinates, text, font=font, anchor=text_anchor)
        text_height = bbox[3] - bbox[1]
    return font


def drawText(idraw, text_id, text, textbox_coordinates, style):
    text_len = len(text)

    if text_id == 'price_kop' or text_id == 'c_price1_kop':
        if text_len == 0:
            text = '00'
        elif text_len == 1:
            text = '0' + text
        elif text_len > 2:
            text = text[:2]

    font_size = int(findStyleValue(style, 'fontSize'))
    font_color = findStyleValue(style, 'fontColor')
    font_family = findStyleValue(style, 'fontFamily')
    font_style_code = findStyleValue(style, 'fontStyle')
    align = findStyleValue(style, 'align')
    vertical_align = findStyleValue(style, 'verticalAlign')

    cursive, weight = getFontStyle(int(font_style_code))

    font_path = getFontPath(font_family, cursive, weight)
    font = ImageFont.truetype(font_path, size=font_size)

    text_width = idraw.textlength(text, font=font)
    textbox_width = textbox_coordinates[2]
    textbox_height = textbox_coordinates[3]

    text_coordinates = getTextCoordinates(textbox_coordinates, align, vertical_align)
    text_anchor = getTextAnchor(align, vertical_align)

    if text_id == 'specification':
        font_size = getFormattedFontSizeByWords(idraw, text, font_path, font_size, textbox_width)
        text, font = getFormattedTextAndFont(idraw, text, font_path, font_size, textbox_width, textbox_height, text_coordinates, text_anchor)

        # font = getFormattedFontByHeight(idraw, text, textbox_height, font_size, font_path, text_coordinates, font, text_anchor)

    else:
        # уменьшаем размер шрифта, если текст шире чем его заданный бокс
        font = getFormattedFontByWidth(idraw, text, text_width, textbox_width, font_size, font_path)
        font = getFormattedFontByHeight(idraw, text, textbox_height, font_size, font_path, text_coordinates, font, text_anchor)

    idraw.text(text_coordinates, text, font=font, fill=font_color, anchor=text_anchor, align=align)

    if isShowDegubLine:
        bbox = idraw.textbbox(text_coordinates, text, font=font, anchor=text_anchor)
        idraw.rectangle(bbox, outline="red")
    # ширина текста bbox[2]-bbox[0]
    # высота текста bbox[3]-bbox[1]

    return text_id, font_size


def getGeometryData(geometry, type=''):
    x = int(float(geometry['x'])) if 'x' in geometry else 0
    y = int(float(geometry['y'])) if 'y' in geometry else 0
    if type == 'text':
        w = int(float(geometry['width']))
        h = int(float(geometry['height']))
    else:
        w = int(geometry['width']) + x
        h = int(geometry['height']) + y
    return x, y, w, h


def getTextCoordinates(size, align, ver_align):
    x, y, w, h = size
    if align == 'left':
        x = x + 3
    if align == 'center':
        x = w / 2 + x
    if align == 'right':
        x = w + x - 3

    if ver_align == 'top':
        y = y + 5
    if ver_align == 'middle':
        y = h / 2 + y
    if ver_align == 'bottom':
        y = h - y - 5

    return x, y, w, h


def getTextAnchor(align, ver_align):
    anchor = ''
    if align == 'left':
        anchor = 'l'
    if align == 'center':
        anchor = 'm'
    if align == 'right':
        anchor = 'r'

    if ver_align == 'top':
        anchor = anchor + 'a'
    if ver_align == 'middle':
        anchor = anchor + 'm'
    if ver_align == 'bottom':
        anchor = anchor + 'b'

    return anchor


def getElId(el):
    for i in el:
        if el[i] == '':
            return i

    return ''


def findStyleValue(style, style_name):
    index_start = style.find(style_name) + len(style_name) + 1
    index_end = style.find(";", index_start)
    if index_end == -1: index_end = len(style)

    if style.find(style_name) == -1 or style[index_start:index_end] == 'default':
        if style_name == 'fontFamily':
            return "Helvetica"
        if style_name == 'fillColor':
            return "#000"
        if style_name == 'fontColor':
            return "#fff"
        if style_name == 'fontSize':
            return "12"
        if style_name == 'fontStyle':
            return 0
        return ''
    else:
        style_data = style[index_start:index_end]
        if style_name == 'fillColor' or style_name == 'fontColor':
            if style_data == '#000000': style_data = '#fff'
            if style_data == '#FFFFFF': style_data = '#000'
        return style_data


def getLabelText(label):
    if label.find('<') > 0:
        print(label)
    else:
        return label


def generateImage(file, specification, price_rub, price_kop, c_price1_rub, c_price1_kop, country='', id_='', date_price='', unit=''):
    tree = ElementTree.parse(file)
    root = tree.getroot()
    xmldict = XmlDictConfig(root)

    price_tag_dict = xmldict['diagram']['mxGraphModel']['root']['mxCell']
    # print(price_tag_dict)
    flag = True

    for el in price_tag_dict:
        el_id = getElId(el)
        # print (el)
        # парсим главный прямоугольник
        if 'parent' in el:
            # mxGeometry
            geometry_data = getGeometryData(el['mxGeometry'])

            # style
            style = el['style']
            fillColor = findStyleValue(style, 'fillColor')

            if flag:
                img = createImage(geometry_data, fillColor)
                # print('Create image. Size:', geometry_data, 'Color:', fillColor)
                idraw = ImageDraw.Draw(img)
                flag = False
            else:
                drawFigure(idraw, geometry_data, fillColor)
                # print('Draw rectangle. Size:', geometry_data, 'Color:', fillColor)
        elif 'label' in el:
            # print(el)

            text = getLabelText(el['label'])
            coordinates = getGeometryData(el['mxCell']['mxGeometry'], 'text')
            style = el['mxCell']['style']

            if 'specification' in el: text = specification

            if 'price_rub' in el: text = price_rub
            if 'price_kop' in el: text = price_kop
            if 'c_price1_rub' in el: text = c_price1_rub
            if 'c_price1_kop' in el: text = c_price1_kop

            if 'country' in el: text = country
            if 'id_' in el: text = id_

            if 'date_price' in el: text = date_price
            if 'unit' in el: text = unit

            if isShowDegubLine:
                geometry_data = getGeometryData(el['mxCell']['mxGeometry'], '')
                idraw.rectangle(geometry_data, outline='black')

            drawText(idraw, el_id, text, coordinates, style)

    img.save('test.bmp')
    return img
