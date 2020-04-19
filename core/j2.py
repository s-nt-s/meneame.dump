import os
import re

import bs4
import json
from jinja2 import Environment, FileSystemLoader

re_br = re.compile(r"<br/>(\s*</)")


def toTag(html, *args):
    if len(args) > 0:
        html = html.format(*args)
    tag = bs4.BeautifulSoup(html, 'html.parser')
    return tag

def millar(value):
    value = "{:,.0f}".format(value).replace(",", ".")
    return value

class Jnj2():

    def __init__(self, origen, destino, pre=None, post=None):
        self.j2_env = Environment(
            loader=FileSystemLoader(origen), trim_blocks=True)
        self.j2_env.filters['millar'] = millar
        self.destino = destino
        self.pre = pre
        self.post = post
        self.lastArgs = None

    def save(self, template, destino=None, parse=None, **kwargs):
        self.lastArgs = kwargs
        if destino is None:
            destino = template
        out = self.j2_env.get_template(template)
        html = out.render(**kwargs)
        if self.pre:
            html = self.pre(html, **kwargs)
        if parse:
            html = parse(html, **kwargs)
        if self.post:
            html = self.post(html, **kwargs)

        destino = self.destino + destino
        directorio = os.path.dirname(destino)

        if not os.path.exists(directorio):
            os.makedirs(directorio)

        with open(destino, "wb") as fh:
            fh.write(bytes(html, 'UTF-8'))
        return html

    def create_script(self, destino, indent=2, replace=False, **kargv):
        destino = self.destino + destino
        if not replace and os.path.isfile(destino):
            return
        separators = (',', ':') if indent is None else None
        with open(destino, "w") as f:
            for i, (k, v) in enumerate(kargv.items()):
                if i > 0:
                    f.write(";\n")
                f.write("var "+k+" = ")
                json.dump(v, f, indent=indent,
                          separators=separators)
                f.write(";")

    def exists(self, destino):
        destino = self.destino + destino
        return os.path.isfile(destino)
