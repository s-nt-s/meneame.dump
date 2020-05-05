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
re_diames= re.compile(r"^\d+-?[efmajasond]$")


def gW(ids, f="id"):
    if len(ids)==1:
        return f+" = "+str(ids.pop())
    return f+" in %s" % (tuple(sorted(ids)), )

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
    if len(tag)==0:
        return None
    tags = tag.split()
    if main and len(tags)>1:
        tags=[parse_tag(t, main=False) or t for t in tags]
        tag = " ".join(t for t in tags if t is not None)
        if len(tag)==0:
            return None
    if main and tag in ("la", "no", "de"):
        return None
    for a, b in (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("à", "a"),
        ("è", "e"),
        ("ì", "i"),
        ("ò", "o"),
        ("ù", "u")
    ):
        tag = tag.replace(a, b)
    if re_diames.match(tag):
        return tag.replace("-", "").upper()
    tag_ori = str(tag)
    tag = tag.lower()
    dot = tag.replace(".", "")
    for a, b in (
        ("ä", "a"),
        ("ë", "e"),
        ("ï", "i"),
        ("ö", "o"),
        ("ü", "u")
    ):
        tag = tag.replace(a, b)
    if tag in ("mujer", "mujeres"):
        return "mujeres"
    if tag in ("hombre", "hombres"):
        return "hombres"
    if dot in ("eeuu", "usa") or tag == "estados unidos":
        return "EE.UU."
    if tag in ("vacuna", "vacunas"):
        return "vacunas"
    if tag in ("viaje", "viajes"):
        return "viajes"
    if tag in ("video", "videos"):
        return "videos"
    if tag in ("gato", "gatos"):
        return "gatos"
    if tag in ("empresa", "empresas"):
        return "empresas"
    if dot == "iu" or tag == "izquierda unida":
        return "IU"
    if tag in ("juego", "juegos"):
        return "juegos"
    if tag in ("medio ambiente", "medioambiente"):
        return "medio ambiente"
    if tag in ("noticia", "noticias"):
        return "noticias"
    if tag in ("nueva york", "new york"):
        return "Nueva York"
    if tag in ("niño", "niños"):
        return "niños"
    if tag in ("niña", "niñas"):
        return "niñas"
    if tag in ("pais vasco", "euskadi"):
        return "Euskadi"
    if dot == "pp" or tag == "partido popular":
        return "PP"
    if dot == "psoe" or tag == "partido socialista obrero español":
        return "PSOE"
    if tag in ("perro", "perros"):
        return "perros"
    if tag in ("peluca", "pelucas"):
        return "pelucas"
    if dot == "ue" or tag == "union europea":
        return "UE"
    if dot == "bce" or tag  == "banco central europeo":
        return "BCE"
    if tag in ("alimentacion", "alimentos"):
        return "alimentos"
    if tag in ("anuncio", "anuncios"):
        return "anuncios"
    if tag in ("padre", "padres"):
        return "padres"
    if dot == "pah" or tag == "plataforma de afectados por la hipoteca":
        return "PAH"
    if tag in ("pension", "pensiones"):
        return "pensiones"
    if tag in ("periodismo", "periodista", "periodistas"):
        return "periodismo"
    if tag in ("pirata", "piratas"):
        return "piratas"
    if tag in ("piso", "pisos"):
        return "pisos"
    if tag in ("porno", "pornografia"):
        return "porno"
    if tag in ("precio", "precios"):
        return "precios"
    if tag in ("premio", "premios"):
        return "premios"
    if tag in ("problema", "problemas"):
        return "problemas"
    if tag in ("profesor", "profesores"):
        return "profesores"
    if tag in ("protesta", "protestas"):
        return "protestas"
    if tag in ("robot", "robots"):
        return "robots"
    if tag in ("salario", "salarios", "sueldo", "sueldos"):
        return "salarios"
    if dot == "uk" or tag == "reino unido":
        return "UK"
    if tag in ("banca", "banco", "bancos"):
        return "bancos"
    if tag in ("blog", "blogs"):
        return "blog"
    if tag in ("avion", "aviones", "aviacion"):
        return "aviones"
    if dot == "avt" or tag == "asociacion victimas del terrorismo":
        return "AVT"
    if tag in ("coche", "coches"):
        return "coches"
    if tag in ("catalunya", "cataluña"):
        return "Cataluña"
    if tag in ("deporte", "deportes"):
        return "deportes"
    if tag in ("droga", "drogas"):
        return "drogas"
    if tag in ("hijo", "hijos"):
        return "hijos"
    if tag in ("hija", "hijas"):
        return "hijas"
    if tag in ("hipoteca", "hipotecas"):
        return "hipotecas"
    if tag in ("homosexual", "homosexuales", "homosexualidad", "gay", "gays"):
        return "homosexualidad"
    if tag in ("foto", "fotografia", "fotografias", "fotos"):
        return "fotos"
    if tag in ("hospital", "hospitales"):
        return "hospitales"
    if tag in ("huelga", "huelga general"):
        return "huelga"
    if tag in ("idioma", "idiomas"):
        return "idiomas"
    if tag in ("iglesia", "iglesia catolica", "iglesias"):
        return "iglesia"
    if tag in ("impuesto", "impuestos"):
        return "impuestos"
    if tag in ("imputado", "imputados"):
        return "imputados"
    if tag in ("incendio", "incendios"):
        return "incendios"
    if tag in ("joven", "jovenes"):
        return "jovenes"
    if tag in ("juez", "jueces"):
        return "jueces"
    if tag in ("ladron", "ladrones"):
        return "ladrones"
    if tag in ("medico", "medicos"):
        return "medicos"
    if tag in ("mentira", "mentiras"):
        return "mentiras"
    if tag in ("militar", "militares"):
        return "militares"
    if tag in ("multa", "multas"):
        return "multas"
    if tag in ("imagen", "imagenes"):
        return "imagenes"
    if tag in ("inmigracion", "inmigrantes"):
        return "inmigracion"
    if tag in ("nazi", "nazis", "nazismo"):
        return "nazismo"
    if tag in ("negocio", "negocios"):
        return "negocios"
    if tag in ("manifestacion", "manifestaciones"):
        return "manifestaciones"
    if tag in ("verguenza", "vergüenza"):
        return "vergüenza"
    if tag in ("abuso", "abusos"):
        return "abuso"
    if tag in ("accidente", "accidentes"):
        return "accidentes"
    if tag in ("amenaza", "amenazas"):
        return "amenazas"
    if tag in ("f1", "formula 1"):
        return "Formula 1"
    if tag in ("futbol", "football"):
        return "futbol"
    if tag in ("peliculas", "pelicula"):
        return "peliculas"
    if tag in ("policia", "policias"):
        return "policia"
    if tag in ("animal", "animales"):
        return "animal"
    if tag in ("arbol", "arboles"):
        return "arboles"
    if tag in ("ayuda", "ayudas"):
        return "ayudas"
    if tag in ("bateria", "baterias"):
        return "baterias"
    if tag in ("colegio", "colegios"):
        return "colegios"
    if tag in ("bicicleta", "bici", "ciclista", "ciclismo"):
        return "bicicleta"
    if tag in ("contrato", "contratos"):
        return "contratos"
    if tag in ("curiosidad", "curiosidades"):
        return "curiosidades"
    if tag in ("declaracion", "declaraciones"):
        return "declaraciones"
    if tag in ("fallece", "fallecimiento", "muere", "muerte", "muerto", "muertos",):
        return "muerte"
    if tag in ("euro", "euros"):
        return "euros"
    if tag in ("hacker", "hackers", "hacking"):
        return "hackers"
    if tag in ("libro", "libros"):
        return "libros"
    if tag in ("mapa", "mapas"):
        return "mapas"
    if tag in ("movil", "moviles"):
        return "moviles"
    if tag in ("ordenador", "ordenadores"):
        return "ordenadores"
    if tag in ("pobres", "pobreza"):
        return "pobreza"
    if tag in ("serie", "series"):
        return "series"
    if tag in ("toro", "toros"):
        return "toros"
    if tag in ("tortura", "torturas"):
        return "torturas"
    if tag in ("venta", "ventas"):
        return "ventas"
    if tag in ("desempleo", "paro"):
        return "paro"
    if tag in ("despido", "despidos"):
        return "despidos"
    if tag in ("detencion", "detenido", "detenidos"):
        return "detenidos"
    if dot in ("tve", "rtve"):
        return "RTVE"
    if dot in ("sms", "sgae", "pnv", "pib", "nsa", "nba", "lhc", "kde", "iss", "iva",
                "ibm", "gnu", "fmi", "facua", "cope", "css", "cnt", "co2", "ciu",
                "cis", "mit", "adn", "aede", "adsl", "ong", "onu", "wtf", "eta", "otan",
                "irpf", "bbc", "bbva", "ccoo", "ugt", "ceoe", "cgt", "cia", "tdt",
                "tv3", "tv", "urss", "vih", "dgt", "ere", "ave", "nasa"):
        return dot.upper()

    if tag == "meneame":
        return "Menéame"
    if tag in ("gurtel", "gürtel"):
        return "Gürtel"
    if tag == "gallardon":
        return "Gallardón"
    if tag == "garzon":
        return "Garzón"
    if tag in ("aznar", "jose maria aznar"):
        return "Aznar"
    if tag in ("cospedal", "maria dolores de cospedal"):
        return "Cospedal"
    if tag in ("camps", "francisco camps"):
        return "Camps"
    if tag in ("franco", "francisco franco"):
        return "Franco"
    if tag in ("obama", "barack obama"):
        return "Obama"
    if tag in ("barcenas", "luis barcenas"):
        return "Bárcenas"
    if tag in ("rajoy", "mariano rajoy", "m rajoy", "m. rajoy", "m.rajoy"):
        return "Rajoy"
    if tag in ("trump", "donald trump"):
        return "Trump"
    if tag in ("anguita", "Julio Anguita"):
        return "Anguita"
    if tag in ("aguirre", "esperanza aguirre"):
        return "Aguirre"
    if tag == "chavez":
        return "Chávez"
    if tag in ("assange", "julian assange"):
        return "Assange"
    if tag in ("cifuentes", "cristina cifuentes"):
        return "Cifuentes"
    if tag in ("pablo iglesia", "pablo iglesias"):
        return "Pablo Iglesias"
    if tag in ("zapatero", "zp"):
        return "Zapatero"
    if tag in ("carmena", "manuela carmena"):
        return "Carmena"
    if tag in ("pdro snchz", "pedro sanchez"):
        return "Pedro Sanchez"
    if tag in ("ana botella", "ignacio gonzalez", "pablo casado", "pedro sanchez", "rita barbera",
            "alonso", "ahora madrid", "podemos", "berlusconi", "bildu", "blesa",
            "bush", "compromis", "david bravo", "feijoo", "felipe gonzalez", "fraga", "gonzalez",
            "juan carlos", "llamazares", "losantos", "merkel", "nadal", "puigdemont", "pujol",
            "putin", "ramoncin", "rubalcaba", "sanchez", "sarkozy", "susana diaz", "urdangarin",
            "villarejo", "vox", "wert", "wyoming", "xunta", "zaplana", "el jueves",
            "el mundo", "el pais", "renfe"):
        return tag.title()
    if tag in ("peru", "el peru"):
        return "Perú"
    if tag == "castilla y leon":
        return "Castilla y Leon"
    if dot == "isis" or tag == "estado islamico":
        return "Isis"
    if tag in ("españa", "europa", "portugal", "alemania", "barcelona", "bilbao", "bolivia", "brasil", "bruselas", "canarias", "china",
            "chile", "colombia", "cuba", "egipto", "francia", "galicia", "india", "inglaterra", "irak", "israel", "italia", "libia",
            "londres", "madrid", "murcia", "palestina", "irlanda", "polonia", "alicante"
            "america", "afganistan", "arabia saudi", "andalucia", "paris", "malaga"
            "almeria", "africa", "turquia", "japon", "iran", "aragon", "argentina", "asturias",
            "australia", "belgica", "berlin", "burgos", "cadiz", "california", "cantabria", "castellon",
            "extremadura", "fukushima", "gaza", "gibraltar", "gijon", "gran bretaña", "granada",
            "grecia", "honduras", "iraq", "islandia", "jaen", "malaga", "mallorca", "marbella",
            "mexico", "navarra", "pakistan", "rusia", "sahara", "salamanca", "santander", "santiago",
            "sevilla", "siria", "somalia", "soria", "suiza", "toledo", "valencia",
            "valladolid", "vaticano", "venezuela", "vigo", "zaragoza", "noruega",
            "roma", "suecia", "ucrania", "marruecos"):
        return tag.title()

    return tag_ori

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
