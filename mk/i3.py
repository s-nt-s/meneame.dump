#!/usr/bin/env python3

from core.j2 import Jnj2
from core.api import Api
from os.path import isfile
from bunch import Bunch
import json
from datetime import datetime
from bs4 import BeautifulSoup
import sys

import argparse

parser = argparse.ArgumentParser(description='Genera el informe sobre Preguntame')
parser.add_argument('--fast', action='store_true', help="No regenera los modelos")
arg = parser.parse_args()

def str_time(val):
    if val == 1:
        return "<code title='1 segundo'>1</code>"
    if val<60:
        return "<code title='{0} segundos'>{0}s</code>".format(val)
    m = int(val/60)
    s = val - (m*60)
    h = int(m/60)
    m = m - (h*60)
    d = int(h/24)
    h = h - (d*24)
    tt = []
    if d == 1:
        tt.append("1 día")
    elif d>1:
        tt.append(str(d)+" días")
    if h == 1:
        tt.append("1 hora")
    elif h>1:
        tt.append(str(h)+" horas")
    if m == 1:
        tt.append("1 minuto")
    elif m>1:
        tt.append(str(m)+" minutos")
    if s==1:
        tt.append("1 segundo")
    elif s>1:
        tt.append(str(s)+" segundos")

    if len(tt)==1:
        title = tt[0]
    else:
        title = ", ".join(tt[:-1])+" y "+tt[-1]
    if val < (60*60):
        rm = round(val/60)
        return "<code title='{0}'>{1}m</code>".format(title, rm)

    hm = '{:02d}:{:02d}'.format(h, m)
    if d==1:
        hm = "1d "+hm
    elif d>1:
        hm = str(d)+"d "+hm
    return "<code title='{0}'>{1}</code>".format(title, hm)

def str_epoch(ts):
    dt = datetime.utcfromtimestamp(ts)
    return dt.strftime('%Y-%m-%d')

def post_soup(html, **kargv):
    soup = BeautifulSoup(html, "lxml")
    for td in soup.findAll("td"):
        code = td.find("code")
        if code:
            title = code.attrs.get("title")
            if title:
                td.attrs["title"]=title
                del code["title"]
    return str(soup)

jHtml = Jnj2("template/", "docs/i3/", post=post_soup)
jHtml.j2_env.filters['str_time'] = str_time
jHtml.j2_env.filters['str_epoch'] = str_epoch

def get_data(file="mk/i3.json"):
    if isfile(file):
        with open(file, "r") as f:
            return json.load(f)
    a=Api()
    data = a.get_list(sub="Pregúntame")
    for i in data:
        i["user"] = dict(a.get_user(i["user"]))
        if i["user"].get("create"):
            i["user"]["create"] = i["user"]["create"].strftime("%Y-%m-%d")
        i["url"] = i["url"].rsplit("?", 1)[0]
        del i["comments"]
        i["comments"] = sorted(a.get_comments(i["id"]), key=lambda c:(c["date"], c["id"]))

    data = sorted(data, key=lambda i:(i["sent_date"], i["id"]))
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
    return data

def set_tt(i):
    if i.id == 2329256:
        i.title = "Ignacio Escolar"
        i.subtt = "Director de eldiario.es"
    if i.id == 2333253:
        i.title = "Tania Sánchez"
        i.subtt = "Candidata por IU a la Comunidad de Madrid"
    if i.id == 2341872:
        i.title = "Pedro J. Ramírez"
        i.subtt = "Periodista"
    if i.id == 2347315:
        i.title = "Alberto Garzón"
        i.subtt = "Candidato a presidente del Gobierno por IU"
    if i.id == 2350836:
        i.title = "Albert Rivera"
        i.subtt = "Presidente de Ciudadanos"
    if i.id == 2357414:
        i.title = "Antonio Miguel Carmona"
        i.subtt = "Candidato del PSOE a la Alcaldía de Madrid"
    if i.id == 2359733:
        i.title = "Mauricio Valiente"
        i.subtt = "Candidato de IU a la alcaldía de Madrid"
    if i.id == 2360393:
        i.title = "Daniel Raventós"
        i.subtt = "Economista"
    if i.id == 2365235:
        i.title = "Isaac Rosa"
        i.subtt = "Escritor"
    if i.id == 2369309:
        i.title = "Elpidio Silva"
        i.subtt = "Abogado y magistrado en excedencia"
    if i.id == 2400821:
        i.title = "Javier Olivares"
        i.subtt = "Guionista y creador de El Ministerio del Tiempo"
    if i.id == 2408909:
        i.title = "Fran Ruíz Antón"
        i.subtt = "Director de Políticas Públicas y Asuntos con Gobierno de Google España y Portugal"
    if i.id == 2412909:
        i.title = "Pablo Echenique"
        i.subtt = "Candidato a la presidencia de Aragón por Podemos"
    if i.id == 2417115:
        i.title = "J. M. Mulet"
        i.subtt = "Profesor de Biotecnología de la UPV e Investigador en el IBMCP"
    if i.id == 2421634:
        i.title = "José Carlos Díez"
        i.subtt = "Economista observador y profesor de economía en Universidad de Alcalá"
    if i.id == 2425667:
        i.title = "Amaia Pérez Orozco"
        i.subtt = "Economista feminista"
    if i.id == 2430010:
        i.title = "Jorge Morales de Labra"
        i.subtt = "Sector eléctrico español"
    if i.id == 2434549:
        i.title = "Miguel Illescas"
        i.subtt = "Gran Maestro Internacional de Ajedrez"
    if i.id == 2438925:
        i.title = "Manel Fontdevila"
        i.subtt = "Humorista gráfico"
    if i.id == 2442614:
        i.title = "Gaby Jorquera"
        i.subtt = "Especialista en exclusión y la pobreza"
    if i.id == 2446394:
        i.title = "Patrícia Soley-Beltran"
        i.subtt = "Doctora en Sociología y exmodelo"
    if i.id == 2449934:
        i.title = "Pedro Duque"
        i.subtt = "Astronauta de la Agencia Espacial Europea"
    if i.id == 2468038:
        i.title = "Eva Belmonte"
        i.subtt = "Autora de El BOE nuestro de cada día"
    if i.id == 2474863:
        i.title = "Pedro Bravo"
        i.subtt = "Periodista en eldiario.es y ctxt.es"
    if i.id == 2477789:
        i.title = "Olga Rodríguez"
        i.subtt = "Periodista en eldiario.es"
    if i.id == 2481332:
        i.title = "Alberto Cairo"
        i.subtt = "Profesor de infografía y visualización de datos en la Universidad de Miami"
    if i.id == 2485200:
        i.title = "Sergio Álvarez Leiva"
        i.subtt = "Fundador y director de Producto de CartoDB"
    if i.id == 2488631:
        i.title = "Fernando Valladares"
        i.subtt = "Investigador del CSIC sobre el cambio climático"
    if i.id == 2489555:
        i.title = "Rosario Vidal"
        i.subtt = "Experta en emisiones de vehículos"
    if i.id == 2492397:
        i.title = "Luis Santamaría"
        i.subtt = "Investigador de la Estación Biológica de Doñana"
    if i.id == 2496912:
        i.title = "Rubén Sánchez"
        i.subtt = "Portavoz de FACUA y autor de #Timocracia"
    if i.id == 2504990:
        i.title = "Empar Pablo Martínez"
        i.subtt = "Responsable de movimientos y redes sociales de CCOO"
    if i.id == 2508068:
        i.title = "Santiago Merino"
        i.subtt = "Director del Museo Nacional de Ciencias Naturales"
    if i.id == 2511455:
        i.title = "Juantxo Lopez de Uralde"
        i.subtt = "Coportavoz de Equo"
    if i.id == 2513846:
        i.title = "Iñigo Sáenz de Ugarte"
        i.subtt = "Subdirector de eldiario.es"
    if i.id == 2515832:
        i.title = "Jose A. Pérez Ledo"
        i.subtt = "Creador y director de Órbita Laika"
    if i.id == 2520836:
        i.title = "Andrés Herzog"
        i.subtt = "Portavoz y Candidato por UPYD a la Presidencia del Gobierno"
    if i.id == 2524058:
        i.title = "Borja Sémper"
        i.subtt = "Candidato al Congreso de los Diputados por el PP de Gipuzkoa"
    if i.id == 2528212:
        i.title = "Teresa Ribera"
        i.subtt = "Directora del Instituto de Desarrollo Sostenible y Relaciones Internacionales (IDDRI)"
    if i.id == 2543734:
        i.title = "Manolis Kogevinas"
        i.subtt = "Investigador en epidemiología ambiental"
    if i.id == 2553715:
        i.title = "Rita Maestre"
        i.subtt = "Portavoz del Ayuntamiento de Madrid"
    if i.id == 2557989:
        i.title = "Daniel Seijo"
        i.subtt = "CEO de Menéame"
    if i.id == 2562005:
        i.title = "Marc Beltran"
        i.subtt = "Experto en Drones"
    if i.id == 2570771:
        i.title = "Teniente Kaffee"
        i.subtt = "Blog ¡Protesto, Señoría!"
    if i.id == 2575439:
        i.title = "María Glez. Veracruz"
        i.subtt = "Diputada nacional por Murcia por el PSOE"
    if i.id == 2576613:
        i.title = "Rebecca Jeschke"
        i.subtt = "Directora de relaciones con los medios y analista de derechos digitales de la EFF"
    if i.id == 2578291:
        i.title = "Joaquín Hortal"
        i.subtt = "Investigador en ecología y biogeografía del CSIC"
    if i.id == 2581975:
        i.title = "Loreto Cascales"
        i.subtt = "Diputada nacional del PP"
    if i.id == 2643649:
        i.title = "Ignacio Escolar"
        i.subtt = "Director de eldiario.es"
    if i.id == 2650358:
        i.title = "David Bravo"
        i.subtt = "Abogado especialista en propiedad intelectual"
    if i.id == 2680796:
        i.title = "Carlos Sánchez Almeida"
        i.subtt = "Socio fundador de Bufet Almeida"
    if i.id == 2686676:
        i.title = "Jairo Mejía"
        i.subtt = "Corresponsal de la agencia EFE en Washington"
    if i.id == 2697602:
        i.title = "Amarna Miller"
        i.subtt = "Actriz y directora porno"
    if i.id == 2729435:
        i.title = "Ángel Sastre"
        i.subtt = "Periodista especializado en zonas en conflicto"
    if i.id == 2736051:
        i.title = "Silvia Barquero"
        i.subtt = "Presidenta de PACMA"
    if i.id == 2741623:
        i.title = "Luis Gil"
        i.subtt = "Biólogo, ingeniero de montes, profesor universitario y miembro de la RAI"
    if i.id == 2750553:
        i.title = "Juan Carlos González"
        i.subtt = "Responsable de medios en Xbox España"
    if i.id == 2752480:
        i.title = "Antonio Martínez Ron"
        i.subtt = "Periodista científico"
    if i.id == 2757923:
        i.title = "Gabriel Rufián"
        i.subtt = "Diputado de ERC en el Congreso"
    if i.id == 2758275:
        i.title = "Enrique Dans"
        i.subtt = "Profesor de innovación en IE Business School"
    if i.id == 2768041:
        i.title = "Jose Cordeiro"
        i.subtt = "Profesor fundador de Singularity University"
    if i.id == 2780110:
        i.title = "Marián García"
        i.subtt = "Dra. Farmacia, nutricionista y divulgadora sanitaria"
    if i.id == 2789700:
        i.title = "Bea Hervella"
        i.subtt = "Meteoróloga"
    if i.id == 2849441:
        i.title = "Santi García Cremades"
        i.subtt = "Matemático y divulgador científico (Órbita Laika, Radio 5)"
    if i.id == 2867855:
        i.title = "Aurora Gonzalez"
        i.subtt = "Secretaria y Portavoz de la Asociación por la Gestación Subrogada en España"
    if i.id == 2940723:
        i.title = "Jimmy Wales"
        i.subtt = "Fundador de Wikipedia y WikiTribune"
    if i.id == 3047112:
        i.title = "Daniele Grasso y Antonio Villarreal"
        i.subtt = "Periodistas y autores de The Implant Files"
    if i.id == 3051919:
        i.title = "José Carlos Rodríguez"
        i.subtt = "Periodista y analista político"
    if i.id == 3068373:
        i.title = "Héctor Socas Navarro"
        i.subtt = "Investigador del Instituto de Astrofísica de Canarias"
    if i.id == 3089750:
        i.title = "David Alandete"
        i.subtt = "Autor de 'Fake News, la nueva arma de destrucción masiva'"
    if i.id == 3110778:
        i.title = "Espido Freire"
        i.subtt = "Escritora"
    if i.id == 3113813:
        i.title = "Mariluz Congosto"
        i.subtt = "Investigadora de datos sociales"
    if i.id == 3118306:
        i.title = "Alberto Rodríguez"
        i.subtt = "Candidato de UP al Congreso por Santa Cruz de Tenerife"
    if i.id == 3150913:
        i.title = "Alfonso López"
        i.subtt = "Cocinero, bloguero y autor de varios libros de cocina"
    if i.id == 3154982:
        i.title = "Paula Barrachina"
        i.subtt = "Portavoz de ACNUR en Libia"
    if i.id == 3161623:
        i.title = "Mamen Jiménez"
        i.subtt = "Psicóloga, sexóloga y terapeuta de pareja"
    if i.id == 3178035:
        i.title = "Elena Gómez-Díaz"
        i.subtt = "Investigadora del CSIC, doctora en Biología y experta en malaria"
    if i.id == 3203777:
        i.title = "María Teresa Pérez"
        i.subtt = "Candidata de UP al Congreso por Alicante"
    if i.id == 3210830:
        i.title = "Ousman Umar"
        i.subtt = "Fundador de la ONG NASCO Feeding Minds"
    if i.id == 3218615:
        i.title = "Álvaro Vizcaíno"
        i.subtt = "Coach, terapeuta, surfista y superviviente"
    if i.id == 3227064:
        i.title = "Gemma del Caño"
        i.subtt = "Farmacéutica y experta en seguridad alimentaria"
    if i.id == 3237987:
        i.title = "Clara Grima"
        i.subtt = "Profesora de matemáticas y divulgadora"
    if i.id == 3246728:
        i.title = "Saúl López"
        i.subtt = "Experto en movilidad eléctrica"
    if i.id == 3253840:
        i.title = "Rodrigo Rivas"
        i.subtt = "Fotógrafo, docente y divulgador"
    if i.id == 3258635:
        i.title = "Juan Gestal Otero"
        i.subtt = "Catedrático de Medicina y Salud Pública"
    if i.id == 3268932:
        i.title = "Jaime Altozano"
        i.subtt = "Youtuber de música"
    if i.id == 3269244:
        i.title = "Remo"
        i.subtt = "Asesor de empresas"
    if i.id == 3276459:
        i.title = "Eduardo Pérez"
        i.subtt = "Psicólogo general sanitario en Madrid"
    if i.id == 3284377:
        i.title = "José Gago y Marcos Saavedra"
        i.subtt = "Cooperavirus"
    if i.id == 3288388:
        i.title = "Jonan Basterra"
        i.subtt = "Periodista y ex paciente de coronavirus en IFEMA"
    if i.id == 3304379:
        i.title = "Antonio Gómez"
        i.subtt = "Nutricionista"
    if i.id == 3309356:
        i.title = "Javi y Marcos"
        i.subtt = "Programadores de la app móvil de Menéame"
    if i.id == 3327486:
        i.title = "Esther Samper"
        i.subtt = "Médica y comunicadora"
    if i.id == 3332042:
        i.title = "Javier Ramírez"
        i.subtt = "Experto en privacidad y seguridad informática"
    if i.id == 3339443:
        i.title = "José Carlos Díez"
        i.subtt = "Economista especializado en macroeconomía"
    if i.id == 3346777:
        i.title = "Beatriz Robles"
        i.subtt = "Tecnóloga de alimentos y dietista-nutricionista"
    if i.id == 3364741:
        i.title = "Rafael Conde"
        i.subtt = "Profesor de Diseño de Videojuegos y Director de Artes Digitales en UCJC"
    if i.id == 3371875:
        i.title = "Contra el Diluvio"
        i.subtt = "Grupo de estudio, reflexión y acción sobre el cambio climático y sus efectos"
    if i.id == 3386107:
        i.title = "Javi Burgos"
        i.subtt = "Científico y gestor"
    if i.id == 3401097:
        i.title = "Óscar Lage"
        i.subtt = "Investigador en ciberseguridad, criptografía y blockchain"
    if i.id == 3408489:
        i.title = "Mikel López Iturriaga"
        i.subtt = "Periodista gastronómico"
    if i.id == 3415195:
        i.title = "Juan Gómez-Jurado"
        i.subtt = "Escritor"
    if i.id == 3422099:
        i.title = "Ricardo Galli"
        i.subtt = "Piloto Ferrari <img alt='' class='icon' src='https://mnmstatic.net/v_149/img/menemojis/36/ferrari.png'/>"
    if i.id == 3429144:
        i.title = "Ramiro Oliva"
        i.subtt = "Unity Asset Store Publisher y fundador de Kronnect"
    if i.id == 3440340:
        i.title = "Andoni Payo"
        i.subtt = "FIFA player para Movistar Riders"
    if i.id == 3448364:
        i.title = "Asier Arranz"
        i.subtt = "Jetson Developer en NVIDIA"
    if i.id == 3456380:
        i.title = "Kike García y Xavi Puig"
        i.subtt = "El Mundo Today"
    if i.id == 3471005:
        i.title = "Rastreadora de COVID"
        i.subtt = "Xunta de Galicia"

data = get_data()
for x, i in enumerate(data):
    i = Bunch(i)
    data[x]=i

    if i.user.get("avatar") is not None and i.id not in (2446394, 2528212):
        i.thumb = i.user["avatar"]
    i.replies = Bunch(
        count=0,
        first=sys.maxsize,
        last=-sys.maxsize,
        words=0
    )
    for c in i.comments:
        if c["user"] == i.user["nick"]:
            i.replies.count = i.replies.count + 1
            i.replies.words = i.replies.words + len(c["content"].strip().split())
            i.replies.first = min(i.replies.first, c["date"])
            i.replies.last = max(i.replies.last, c["date"])
    i.questions = len([c for c in i.comments if c["date"]<=i.replies.last])
    i.questions = i.questions - i.replies.count
    set_tt(i)

jHtml.save("i3.html",
    destino="index.html",
    data=data
)
