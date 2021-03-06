r"""
______                  _   _  __       _ 
| ___ \                | | (_)/ _|     | |
| |_/ / ___  __ _ _   _| |_ _| |_ _   _| |
| ___ \/ _ \/ _` | | | | __| |  _| | | | |
| |_/ /  __/ (_| | |_| | |_| | | | |_| | |
\____/ \___|\__,_|\__,_|\__|_|_|  \__,_|_|
 _____ _                                  
/  __ \ |                          ______
| /  \/ |__   ___   ___ ___       /_/_/_/
| |   | '_ \ / _ \ / __/ _ \     /_/_/_/
| \__/\ | | | (_) | (_| (_) |   /_/%/%/
 \____/_| |_|\___/ \___\___/   /%/%/%/

                        by tasuren
"""


version = "1.0.0"


class BeautifulChoco():
    def __init__(self, html):
        self.spaces = '\x20\x0a\x09\x0c\x0d\n\r\t\u3000'
        if isinstance(html, list):
            self.html = html[0]
            self.default = html[1]
        else:
            self.default = self.html_parser(html)
            self.html = self.default + []

    def html_parser(self, html) -> list:
        now_string = False
        now_elements = ""
        before_less_than_sign = False

        elements = []
        characters = ""

        for char in html:
            characters += char
            if char == '"':
                now_string = False if now_string else True
            elif char in self.spaces and not now_string and not now_element:
                characters = characters[:-1]
            elif char == "<" and not now_string:
                now_element = True
                before_less_than_sign = True
            elif char == ">" and not now_string:
                now_element = False
                elements.append(characters)
                characters = ""
            elif char == "/" and not now_string and not before_less_than_sign:
                depth += 1
                text = characters[:-2]
                if text:
                    elements.append(text)
                    characters = "</"
            if char != ">":
                before_less_than_sign = False

        return elements

    def attributes_parser(self, element) -> dict:
        now_element_name = True
        now_string = False
        now_attribute = ""

        characters = ""
        attributes = {}

        count = -1
        for char in element[element.find("<"):element.rfind(">")]+" ":
            characters += char
            count += 1

            if char != " " and char in self.spaces and not now_string:
                char = " "

            if char == " " and not now_string:
                if now_element_name:
                    now_element_name = False
                    characters = ""
                else:
                    attributes[now_attribute] = characters[1:-2]
                    characters = ""
            elif char == '"':
                now_string = False if now_string else True
            elif char == "=" and not now_string:
                now_attribute = characters[:-1]
                attributes[now_attribute] = ""
                characters = ""

        return attributes

    def find(self, check_tag:str, attributes:dict={}, get_all=False) -> list or None or BeautifulChoco:
        super_elements = []
        elements = []
        items = []
        # 範囲要素リスト
        # 範囲要素リストについては最終チェックの中にある。
        force_append = []

        attributes = list(attributes.items())

        # 検索を開始する。
        for element in self.html:
            # 要素の追加。
            if element[0] == "<" and len(element) > 3:
                if element[1] != "/":
                    # 範囲要素リストが空でないならまだ追加したやつの範囲になっている。
                    # だからその場合は追加する。
                    # 範囲要素リストについては最終チェックの中にある。
                    if force_append:
                        elements.append(element)
                    else:
                        # タグ名を取り出す。
                        tag = element[1:element.find(" ")]
                        # 属性を取り出す。
                        parsed_attributes = self.attributes_parser(element)
                        # 属性のアイテムがあっているか確認する。
                        # 指定がない場合はTrueのままでスルーする。
                        item_bool = True
                        if attributes:
                            item_bool = False
                            for pattribute,pitem in list(parsed_attributes.items()):
                                for attribute,item in attributes:
                                    ritem = item+"|"
                                    # 関数に対応するため関数じゃない文字列とリストは関数になおす。
                                    if isinstance(item, str):
                                        item = eval(f"lambda value: value == '{item}'")
                                    elif isinstance(item, list):
                                        item = eval(f"lambda value: value in {item}")
                                    # チェックをする。
                                    if pattribute == attribute and item(pitem):
                                        item_bool = True
                                        break
                                if item_bool:
                                    break
                        # 最終チェック。
                        if check_tag == tag and item_bool:
                            elements.append(element)
                            # もしimgのような単独の要素じゃないなら、その要素の範囲を全て取らないといけない。
                            # そのためもしそれの場合ならその要素の名前を範囲要素リストに追加する。
                            # そしてその範囲要素リストに要素がから出ない場合は常に追加するようにする。
                            # これで範囲を全て取ることができる。
                            if f"</{tag}>" in self.default[self.default.index(element):]:
                                force_append.append(tag)
                            else:
                                # もしimgのような単独の要素ならそのまま親のリストに追加する。
                                # これは範囲の終わりに親のリストに要素を追加方式だからである。
                                # imgのような単独の要素は範囲がないため親リストに追加できずに終わってしまう。
                                # それを防ぐためである。
                                super_elements.append(
                                    BeautifulChoco([elements, self.default])
                                )
                                elements = []
                else:
                    # タグ名を取り出す。
                    tag = element[2:-1]
                    # 追加したやつリストが空でないならまだ追加したやつの範囲になっている。
                    # だからその場合は追加する。
                    if force_append:
                        elements.append(element)
                    # もし追加したやつリストにタグがあるならそれは削除する。
                    # よって範囲が終了したことをしめす。
                    # そしてその範囲を親のリストに追加する。
                    if tag in force_append:
                        force_append.remove(tag)
                        super_elements.append(BeautifulChoco([elements, self.default]))
                        elements = []

                # get_all(全て取得)がFalseでもう既に取得されているなら終わりにする。
                if not get_all and super_elements:
                    return super_elements[0]
            else:
                if force_append:
                    elements.append(element)

        # get_all(全て取得)がFalseなら１つ目を返す。
        # ないならNoneを返す。
        if not get_all:
            return super_elements[0] if super_elements else None

        return super_elements


    @property
    def attributes(self) -> dict:
        return self.attributes_parser(self.html[0]) if self.html else {}

    def get(self, attribute) -> str or None:
        attribute = self.attributes_parser(self.html[0]).get(attribute) if self.html else None
        return attribute if attribute else None

    @property
    def text(self) -> list:
        texts = []
        for element in self.html:
            if not element.startswith("<"):
                texts.append(element)

        return texts