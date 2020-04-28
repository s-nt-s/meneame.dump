import yaml
from glob import glob
import os
import re
import argparse
from urllib.parse import urlparse

re_sp = re.compile(r"\s+")
re_www = re.compile(r"^www\d*\.")
re_nb = re.compile(r"\d+")
re_blogspot = re.compile(r"\.blogspot\.com\.[a-z]{,2}$")
re_port = re.compile(r":\d+$")

def chunks(lst, n):
    arr = []
    for i in lst:
        arr.append(i)
        if len(arr)==n:
            yield arr
            arr = []
    if arr:
        yield arr

def read_yml_all(*fls):
    if len(fls)==1 and "*" in fls[0]:
        fls=sorted(glob(fls[0]))
    for fl in fls:
        if os.path.isfile(fl):
            with open(fl, 'r') as f:
                for i in yaml.load_all(f, Loader=yaml.FullLoader):
                    yield i

def readlines(*fls):
    if len(fls)==1 and "*" in fls[0]:
        fls=sorted(glob(fls[0]))
    for fl in fls:
        if os.path.isfile(fl):
            with open(fl, 'r') as f:
                for i in f.readlines():
                    i = i.strip()
                    if i:
                        yield i

def parse_tag(tag, main=True):
    tag = re_sp.sub(" ", tag).strip()
    while main and len(tag)>2 and (tag[0]+tag[-1]) in ("''", '""', "``", "´´", "`´", "´`", "[]", "()"):
        tag = tag[1:-1]
    if len(tag)==0 or (main and len(tag)<2):
        return None
    tags = tag.split()
    if main and len(tags)>1:
        tags=[parse_tag(t, main=False) or t for t in tags]
        tag = " ".join(t for t in tags if t is not None)
        if len(tag)==0:
            return None
    original = str(tag)
    for a, b in (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u")
    ):
        tag = tag.replace(a, b)
    if main and tag in ("de", "la"):
        return None
    if tag == "meneame":
        return "Menéame"
    if tag == "monarquia":
        return "monarquía"
    if tag in ("mujer", "mujeres"):
        return "mujeres"
    if tag in ("hombre", "hombres"):
        return "hombres"
    if tag in ("15-m", "15m"):
        return "15M"
    if tag in ("11-m", "11m"):
        return "11M"
    if tag in ("ee.uu", "ee.uu.", "eeuu", "eeuu.", "u.s.a.", "estados unidos"):
        return "EE.UU."
    if tag in ("eta", "e.t.a.", "eta."):
        return "ETA"
    if tag == "evolucion":
        return "evolución"
    if tag == "fiscalia":
        return "fiscalía"
    if tag in ("f1", "formula 1"):
        return "Fórmula 1"
    if tag in ("futbol", "football"):
        return "fútbol"
    if tag == "fotografia":
        return "fotografía"
    if tag == ("gato", "gatos"):
        return "gatos"
    if tag in ("empresa", "empresas"):
        return "empresas"
    if tag == "gallardon":
        return "Gallardón"
    if tag == "garzon":
        return "Garzón"
    if tag in ("gurtel", "gürtel"):
        return "Gürtel"
    if tag == "imagenes":
        return "imágenes"
    if tag == "informacion":
        return "información"
    if tag == "informatica":
        return "informática"
    if tag == "inmigracion":
        return "inmigración"
    if tag == "inversion":
        return "inversión"
    if tag == "investigacion":
        return "investigación"
    if tag == "iran":
        return "Irán"
    if tag in ("iu", "iu.", "i.u."):
        return "IU"
    if tag == "japon":
        return "Japón"
    if tag in ("juego", "juegos"):
        return "juegos"
    if tag == "manifestacion":
        return "manifestación"
    if tag == "manipulacion":
        return "manipulación"
    if tag == "matematicas":
        return "matemáticas"
    if tag in ("medio ambiente", "medioambiente"):
        return "medio ambiente"
    if tag == "musica":
        return "música"
    if tag in ("niño", "niños"):
        return "niños"
    if tag in ("niña", "niñas"):
        return "niñas"
    if tag == "malaga":
        return "Málaga"
    if tag in ("noticia", "noticias"):
        return "noticias"
    if tag in ("nueva york", "new york"):
        return "Nueva York"
    if tag == "opinion":
        return "opinión"
    if tag in ("otan", "otan.", "o.t.a.n."):
        return "OTAN"
    if tag == "pablo iglesias":
        return "Pablo Iglesias"
    if tag in ("pais vasco", "euskadi"):
        return "Euskadi"
    if tag in ("pp", "pp.", "p.p.", "partido popular"):
        return "PP"
    if tag in ("psoe", "psoe.", "p.s.o.e.", "partido socialista obrero español"):
        return "PSOE"
    if tag in ("peliculas", "pelicula"):
        return "películas"
    if tag in ("perro", "perros"):
        return "perros"
    if tag in ("peluca", "pelucas"):
        return "pelucas"
    if tag in ("peru", "el peru"):
        return "Perú"
    if tag == "petroleo":
        return "petróleo"
    if tag == "pirateria":
        return "piratería"
    if tag in ("policia", "policias"):
        return "policía"
    if tag == "politica":
        return "política"
    if tag == "politicos":
        return "políticos"
    if tag == "paris":
        return "París"
    if tag == "prision":
        return "prisión"
    if tag == "privatizacion":
        return "privatización"
    if tag == "programacion":
        return "programación"
    if tag == "psicologia":
        return "psicología"
    if tag == "referendum":
        return "referéndum"
    if tag == "religion":
        return "religión"
    if tag == "represion":
        return "represión"
    if tag == "republica":
        return "república"
    if tag == "revolucion":
        return "revolución"
    if tag == "tecnologia":
        return "tecnología"
    if tag == "telefonica":
        return "telefónica"
    if tag == "television":
        return "televisión"
    if tag == "turquia":
        return "Turquía"
    if tag in ("ue", "u.e.", "ue.", "union europea"):
        return "UE"
    if tag == "violacion":
        return "violación"
    if tag == "africa":
        return "África"
    if tag in ("españa", "europa", "portugal", "alemania", "aznar", "barcelona", "bilbao", "bolivia", "brasil", "bruselas", "canarias", "china", "chile", "colombia", "cospedal", "camps", "cuba", "egipto", "francia", "franco", "galicia", "india", "inglaterra", "irak", "israel", "italia", "libia", "londres", "madrid", "murcia", "obama", "palestina", "rajoy", "reino unido", "trump"):
        return tag.title()
    if tag == "andalucia":
        return "Andalucía"
    if tag == "energia":
        return "energía"
    if tag == "arqueologia":
        return "arqueología"
    if tag == "articulo":
        return "artículo"
    if tag == "astronomia":
        return "astronomía"
    if tag == "biologia":
        return "biología"
    if tag == "avion":
        return "avión"
    if tag in ("banca", "banco", "bancos"):
        return "bancos"
    if tag in ("blog", "blogs"):
        return "blog"
    if tag in ("barcenas", "luis barcenas"):
        return "Bárcenas"
    if "climatico" in tag:
        return tag.replace("climatico", "climático")
    if tag in ("catalunya", "cataluña"):
        return "Cataluña"
    if tag == "chavez":
        return "Chávez"
    if tag in ("coche", "coches"):
        return "coches"
    if tag == "comunicacion":
        return "comunicación"
    if tag == "construccion":
        return "construcción"
    if tag == "contaminacion":
        return "contaminación"
    if tag == "corrupcion":
        return "corrupción"
    if tag == "critica":
        return "crítica"
    if tag == "democracia":
        return "democracía"
    if tag in ("deporte", "deportes"):
        return "deportes"
    if tag == "dimision":
        return "dimisión"
    if tag in ("droga", "drogas"):
        return "drogas"
    if tag == "ecologia":
        return "ecología"
    if tag == "economia":
        return "economía"
    if tag == "educacion":
        return "educación"
    return original

def extract_tags(tags):
    tags = tags.lower().strip().split(",")
    tags = set(t.strip() for t in tags if t.strip())
    tags = set([parse_tag(t) for t in tags])
    tags = sorted(t for t in tags if t is not None)
    return tags

def mkArg(title, **kargv):
    parser = argparse.ArgumentParser(description=title)
    for k, h in kargv.items():
        if len(k)==1:
            k = "-" + k
        else:
            k = "--" + k
        parser.add_argument(k, action='store_true', help=h)
    args = parser.parse_args()
    if "silent" in kargv:
        args.trazas = not args.silent
    return args

def extract_domain(url):
    if not url or url in ("[borrado a petición del usuario]", "blank.html") or url.startswith("about:"):
        return None
    if re_www.search(url):
        url = "http://"+url
    dom = urlparse(url).netloc
    if not dom or not dom.strip():
        return None
    dom = dom.strip().lower()
    dom = re_port.sub("", dom)
    dom = re_www.sub("", dom).rstrip(".")
    dom = re_blogspot.sub(".blogspot.com", dom)
    while True:
        spl = dom.split(".")
        sz = len(spl)
        if sz<3 or len(spl[0])>2 or re_nb.search(spl[0]):
            break
        tail = ".".join(spl[-2:])
        if sz==3 and (len(tail)<7 or spl[-2] == "google"):
            break
        dom = ".".join(spl[1:])
    return dom
