import os
import re

import bs4
import json
from jinja2 import Environment, FileSystemLoader
from glob import iglob
from os.path import relpath

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
        self.resources = [self.destino]

    def _find(self, glb, recursive=True):
        arr=[]
        for r in self.resources:
            for i in iglob(r+glb, recursive=recursive):
                arr.append(relpath(i, self.destino))
        return sorted(arr)

    @property
    def javascript(self):
        return self._find("/**/*.js")

    @property
    def css(self):
        return self._find("/**/*.css")

    def save(self, template, destino=None, parse=None, **kwargs):
        self.lastArgs = kwargs
        if destino is None:
            destino = template
        out = self.j2_env.get_template(template)
        html = out.render(**kwargs, javascript=self.javascript, css=self.css)
        if self.pre:
            html = self.pre(html, **kwargs)
        if parse:
            html = parse(html, **kwargs)

        if destino.endswith(".html") and (self.javascript or self.css):
            soup = bs4.BeautifulSoup(html, 'lxml')
            remo = []
            for j in self.javascript:
                items = soup.select("script[src='"+j+"']")
                if len(items)>1:
                    remo.extend(items)
            for c in self.css:
                items = soup.select("link[href='"+c+"']")
                if len(items)>1:
                    remo.extend(items)
            for r in remo:
                if r.attrs.get("data-autoinsert"):
                    r.extract()
            html = str(soup)

        if self.post:
            html = self.post(html, **kwargs)

        destino = self.destino + destino
        directorio = os.path.dirname(destino)

        if not os.path.exists(directorio):
            os.makedirs(directorio)

        with open(destino, "wb") as fh:
            fh.write(bytes(html, 'UTF-8'))
        return html

    def create_script(self, destino, indent=1, replace=False, **kargv):
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
