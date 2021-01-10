# Objetivo

Extraer todos los enlaces, comentarios y posts de meneame.net cuyo
tiempo de edición ya haya pasado.

# Metodología

## Descubrimiento de endopoints

Con [endpoint.py](/core/endpoint.py) buscamos en el
[código fuente de Menéame](https://github.com/Meneame/meneame.net/)
las rutas que nos puedan servir de `endpoint` para extraer datos.

En resultado se puede ver en [endpoint.py - README.md](/core/README.md).

## Selección de endopoints

Finalmente nos quedamos con:

* [meneame.net/api/list.php?id=](https://www.meneame.net/api/list.php?id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/api/list.php">c</a>
</sup> para comentarios
* [meneame.net/api/list.php?status=queued&row=1](https://www.meneame.net/api/list.php?status=queued&rows=1)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/api/list.php">c</a>
</sup> para obtener la última noticia
* [meneame.net/backend/info.php](https://www.meneame.net/backend/info.php?what=&fields=&id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/backend/info.php">c</a>
</sup> para obtener noticias y posts, y usuarios de comentarios
* [meneame.net/backend/get_user_info.php](https://www.meneame.net/backend/get_user_info.php?id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/backend/get_user_info.php">c</a>
</sup> para obtener información de los usuarios

## Operativa

### Fecha de corte

Primero obtenemos la fecha de corte
(antes de ella todos los contenidos están consolidados, después puede que sufran cambios)
consultando el campo `sent_date` de la última noticia (vía [meneame.net/api/list.php?status=queued&row=1](https://www.meneame.net/api/list.php?status=queued&rows=1)),
restandole el mayor campo `*time*` de [la configuración de Menéame](https://github.com/Meneame/meneame.net/blob/master/www/config.php) (cuando se escribe esto dicho valor es `10 días`), y restandole
otro día adicional por si acaso.

De ahora en adelante, todos los datos recuperados solo se guardaran en la base
de datos si su fecha es inferior a la fecha de corte anteriormente definida.

### Noticias

Para obtener las noticias usaremos:

* [meneame.net/backend/info.php?&what=link&id=1&fields=clicks,content,date,karma,negatives,sent_date,status,sub_name,tags,title](https://www.meneame.net/backend/info.php?&what=link&id=1&fields=clicks,content,date,karma,negatives,sent_date,status,sub_name,tags,title)
* [meneame.net/backend/info.php?&what=link&id=1&fields=url,username,votes,comments,sub_status,sub_status_id,sub_status_origen,sub_karma,author](https://www.meneame.net/backend/info.php?&what=link&id=1&fields=url,username,votes,comments,sub_status,sub_status_id,sub_status_origen,sub_karma,author)
* [meneame.net/backend/info.php?&what=link&id=1&fields=anonymous](https://www.meneame.net/backend/info.php?&what=link&id=1&fields=anonymous)

Siendo `1` el `id` de la noticia en cuestión. (Nota: hay que hacerlo en varias llamadas porque el `endpoint` no acepta más de 10 valores en el parámetro `fields`)

Haremos esto por cada id entre `1` y el de la última noticia.

### Comentarios

Para las noticias consultaremos [meneame.net/api/list.php?id=1](https://www.meneame.net/api/list.php?id=1) siendo `1` el `id` de la noticia para la cual
queremos recuperar los comentarios.

Para completar la información con el `id` del usuario que hizo el comentario,
usaremos [meneame.net/backend/info.php?&what=comment&id=1&fields=author](meneame.net/backend/info.php?&what=comment&id=1&fields=author) donde `1` es el id del comentario.

Este paso nos lo podemos ahorrar si el nick devuelto en el primer `endpoint`
es del tipo `--XXXXX--` donde `XXXXX` es un número, porque en tal caso
se trata de un usuario eliminado y `XXXXX` es el `id`.

### Posts

Para los posts tendremos que obtener el `id` del último posts
[directamente de la web](https://www.meneame.net/notame/), y luego
consultar desde `1` hasta ese último `id` la información de cada
post con [meneame.net/backend/info.php?&what=posts&id=1&fields=date,author,karma,votes](https://meneame.net/backend/info.php?&what=comment&id=1&fields=date,author,karma,votes)
donde `1` es del `id` de cada post.

### Usuarios

De entre todos los datos anteriores buscamos el `id` de usuario más alto y
recorremos desde `1` a ese `id` consultando [meneame.net/backend/get_user_info.php?id=1](https://www.meneame.net/backend/get_user_info.php?id=1) donde `1` es el `id` del usuario.

# Scripts

Todo esto se condensa en:

* [`history.py`](/history.py): recupera el histórico de noticias
* [`comments.py`](/comments.py): obtiene los comentarios de las noticias
* [`posts.py`](/posts.py): obtiene los posts
* [`python3 -m core.db users`](/core/db.py): inserta y actualiza usuarios
* [`python3 -m core.db tags`](/core/db.py): inserta y actualiza tags
* [`general.sql`](/sql/views/general.sql): crea una tabla con la edición general de Meneame
* [`actividad.sql`](/sql/views/actividad.sql): crea una tabla con la actividad de los usuarios

# Conclusiones

Aunque la api de Menéame ofrece mucha información, tiene limitaciones para
evitar el `abuso` (o eso parece) que consiguen el efecto contrario, ya que provocan que para
poder obtener toda la información disponible necesites una cantidad brutal de
llamadas a la api.

A modo de ejemplo: si tenemos 3.000.000 de noticias, 30.000.000 comentarios,
600.000 usuarios y 2.000.000 posts (menos de lo que ya hay)
tendremos que hacer entre 14.600.000 y 44.600.000 llamadas.

Ayudaría enormemente eliminar la restricción de 10 valores para el parámetro `fields`
en el `endpoint` `meneame.net/backend/info.php`. Esta limitación no tiene
sentido ya que no impide la consulta a la base de datos ni tampoco influye
en cuantos campos se recuperan en dicha consulta ya que el campo `fields` solo se
usa después para copiar a un `json` solo los campos solicitados
o devolviendo un objeto vació si solicitaste más de 10
campos. En cualquier caso, para entonces el trabajo pesado ya se ha hecho.

Otra modificación que ahorraría muchas llamadas sería dar el `user_id`
en el `endopoint` `meneame.net/api/list.php` y no solo su `nick`.

Estos dos cambios permitirían obtener los datos de nuestro ejemplo con
8.600.000 llamadas.

Por otro lado seria muy recomendable crear una sección `descargas`
y proporcionar periódicamente (quizá una vez al año) un volcado de la base de datos
(no entera, claro, si no solo la parte que ya se esta dando vía api)
de manera que solo haga falta usar la api para el último periodo no cubierto.

Esto reduciría enormemente la presión a la que deben verse sometidos los servidores
de Menéame cada vez que alguien quiere hacer algún estudio de sus datos.
Recordemos que hablamos de información que ya esta siendo ofrecida (vía api) y
por lo tanto no hay ninguna razón para dificultar su acceso, sobre todo cuando
esta dificultad no impide su obtención si no que simplemente provoca
freír Menéame a llamadas `HTTP`.

# ¿No hay una mejor manera?

En la [v2](https://github.com/s-nt-s/meneame.dump/blob/v2/README.md) se describe
una aproximación que intenta hacer muchas menos llamadas a la api.
Puedes consultarla
[en dicha versión](https://github.com/s-nt-s/meneame.dump/blob/v2/README.md)
para sacar ideas,
yo la termine descartando porque al final siempre necesitaba algún
campo que solo se pueden obtener con `meneame.net/backend/info.php`.
