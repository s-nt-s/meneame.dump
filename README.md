# Objetivo

Extraer todos los enlaces y comentarios de meneame.net,
en especial aquellos que ya han sido cerrados.

# Metodología

## Descubrimiento de endopoints

Con [endpoint.py](/core/endpoint.py) buscamos en el
[código fuente de meneame](https://github.com/Meneame/meneame.net/)
las rutas que nos puedan servir de `endpoint` para extraer datos.

En resultado se puede ver en [endpoint.py - README.md](/core/README.md).

## Selección de endopoints

Finalmente nos quedamos con:

* [meneame.net/api/list.php](https://www.meneame.net/api/list.php)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/api/list.php">c</a>
</sup> para obtener las noticias y comentarios
* [meneame.net/backend/info.php](https://www.meneame.net/backend/info.php?what=&fields=&id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/backend/info.php">c</a>
</sup> para obtener noticias
* [meneame.net/backend/get_user_info.php](https://www.meneame.net/backend/get_user_info.php?id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/backend/get_user_info.php">c</a>
</sup> para obtener ids de usuarios

## Operativa

La manera de obtener el mayor número de noticias recientes, en el menor número de llamadas,
sera invocar el `endpoint` [meneame.net/api/list.php](https://www.meneame.net/api/list.php)
por cada estado posible solicitando el máximo de resultados que permite la api. Es decir:

* [meneame.net/api/list.php?rows=2000&status=published](https://www.meneame.net/api/list.php?rows=2000&status=published)
* [meneame.net/api/list.php?rows=2000&status=queued](https://www.meneame.net/api/list.php?rows=2000&status=queued)
* [meneame.net/api/list.php?rows=2000&status=all](https://www.meneame.net/api/list.php?rows=2000&status=all)
* [meneame.net/api/list.php?rows=2000&status=autodiscard](https://www.meneame.net/api/list.php?rows=2000&status=autodiscard)
* [meneame.net/api/list.php?rows=2000&status=discard](https://www.meneame.net/api/list.php?rows=2000&status=discard)
* [meneame.net/api/list.php?rows=2000&status=abuse](https://www.meneame.net/api/list.php?rows=2000&status=abuse)
* [meneame.net/api/list.php?rows=2000&status=duplicated](https://www.meneame.net/api/list.php?rows=2000&status=duplicated)
* [meneame.net/api/list.php?rows=2000&status=metapublished](https://www.meneame.net/api/list.php?rows=2000&status=metapublished)

A efectos práctios `all` es como buscar `published` y `queued` a la vez, mientras que `duplicated` y `metapublished` nunca
dan resultados, por lo tanto consultando todos estos `endpoint` obtendremos 10.000 noticias.

Nota: Supuestamente podriamos hacer lo mismo con cada sub, primero recuperando los subs con el endpoint [meneame.net/backend/get_subs.php](https://www.meneame.net/backend/get_subs.php) y despues usando el parametro `sub` del endpoint `meneame.net/api/list.php`, pero [por alguna extraña razón nunca devuelve nada](https://github.com/Meneame/meneame.net/issues/28).

A la vez que hacemos esto resolveremos todos los `ids` de los usuarios que enviaron esas noticias:

* Aquellos usuarios cuyo nick sea `--XXXXXXX--` (siendo `XXXXXXX` un número) son usuarios eliminados que tenian por `id` `XXXXXXX`
* Para el resto consultaremos [meneame.net/backend/get_user_info.php?id=gallir](https://www.meneame.net/backend/get_user_info.php?id=gallir) (donde `gallir` es el usuario que queremos consultar) y si hay suerte ese usuario
tendrá un avatar, cuyo nombre de fichero sera `XXXXXXX-YYYYY-ZZ.jpg` siendo todas las letras números y `XXXXXXX` el id
del usuario.

Una vez hecho esto, intentamos recuperar todo el histórico mediante dos métodos:

Primero, tomamos el `id` de usuario más alto que hayamos obtenido hasta el momento y luego recorremos todo el intervalo desde ese número a 1 solicitando
las últimas 2.000 noticias de cada usuario vía [meneame.net/api/list.php?rows=2000&sent_by=1](https://www.meneame.net/api/list.php?rows=2000&sent_by=1) (siendo `1` el `id` del usuario).

Después, consultaremos una a una las noticias que aún no tenemos vía:

* [meneame.net/backend/info.php?&what=link&id=1&fields=clicks,content,date,karma,negatives,sent_date,status,sub_name,tags,title](https://www.meneame.net/backend/info.php?&what=link&id=1&fields=clicks,content,date,karma,negatives,sent_date,status,sub_name,tags,title)
* [meneame.net/backend/info.php?&what=link&id=1&fields=url,username,votes,comments,sub_status,sub_status_id](https://www.meneame.net/backend/info.php?&what=link&id=1&fields=url,username,votes,comments,sub_status,sub_status_id)

Siendo `1` el `id` de la noticia en cuestión. (Nota: hay que hacerlo en dos llamadas porque el `endpoint` no acepta más de 10 valores en el parámetro `fields`)

*¿Por qué recupero tambien los campos `sub_status` y `sub_status_id`?* Porque a diferencia de lo que recuperamos con `meneame.net/api/list.php` ahora estaremos obteniendo tambien resultados de los `subs` y el estado que obtenemos en `status` describe al enlace en su `sub` no en la portada general, para saber si el enlace ha sido promocionado de su `sub` a la cola o portada general necesitamos los valores de `sub_status` y `sub_status_id`.

Una vez llegado aquí, para obtener los comentarios basta con usar el `endpoint` [meneame.net/api/list.php?rows=2000&id=1](https://www.meneame.net/api/list.php?rows=2000&id=1) (donde `1` es el `id` de la noticia).
No he considerado necesario buscar un método para obtener comentarios más allá de
los primeros 2.000 ya que es harto improbable que una noticia llegue a tener tantos, solo he visto 6 casos y es por troleo:

* [noticia 295646](https://www.meneame.net/story/295646/standard/28)
* [noticia 367530](https://www.meneame.net/story/367530/standard/28)
* [noticia 409113](https://www.meneame.net/story/409113/standard/28)
* [noticia 414633](https://www.meneame.net/story/414633/standard/28)
* [noticia 661049](https://www.meneame.net/story/661049/standard/28)
* [noticia 1001344](https://www.meneame.net/story/1001344/standard/28)

## Mantener actualizada la base de datos

Una vez terminados los pasos anteriores podemos obtener de
[config.php](https://github.com/Meneame/meneame.net/blob/master/www/config.php)
el valor de `time_enabled_comments` y restarselo al valor máximo
del atributo `sent_date` de los enlaces obtenidos, de manera que sabremos
que todos los enlaces con un valor `sent_date` menor al valor obtenido
en la resta son enlaces cerrados y por lo tanto ya tenemos toda su información
definitiva.

¿Pero que pasa con los enlaces con `sent_date` mayor al valor de corte anteriormente
definido? Estas serán noticias que aún no estaban cerradas cuando las consultamos y por lo tanto pueden haber cambiado. En ese caso tenemos dos opciones:

* Descartarlas de nuestro análisis
* Actualizarlas más tarde

Para actualizarlas podemos repetir la operativa anterior (aunque esto hará que
volvamos a capturar noticias no cerradas) o pedir sus datos, una a una, con
el `endpoint` [meneame.net/backend/info.php](https://www.meneame.net/backend/info.php?what=&fields=&id=)<sup>
<a href="https://github.com/Meneame/meneame.net/blob/master/www/backend/info.php">c</a>
</sup>

# Scripts

Todo esto se condensa en:

* [`last.py`](/last.py): obtiene las últimas noticias y actualiza las que pueden haberse
cerrado entre ese momento y la anterior actualización
* [`history.py`](/history.py): recupera el histórico de noticias antiguas
* [`comments.py`](/comments.py): obtiene los comentarios de las noticias cerradas

# Conclusiones

Aunque la api de meneame ofrece muchas información esta llena de limitaciones para
evitar el `abuso` que consiguen el efecto contrario, ya que provocan que para
poder obtener toda la información disponible necesites mínimo 3 llamadas a la
api por enlace + 2 por cada usuario, lo que (si tenemos
3.000.000 de noticias, 600.000 usuarios) hace 10.200.000 llamadas.

Creo sinceramente que seria mucho más razonable crear una sección `descargas`
y proporcionar periódicamente (quizá una vez al año) un volcado de la base de datos
(no entera, claro, si no solo la parte que ya se esta dando vía api y solo de los
  enlaces ya cerrados) de manera que solo haga falta usar la api para el último periodo no cubierto.

Esto reduciría enormemente la presión a la que deben verse sometidos los servidores
de meneame cada vez que alguien quiere hacer algún estudio de sus datos.
Recordemos que hablamos de información que ya esta siendo ofrecida (vía api) y
por lo tanto no hay ninguna razón para dificultar su acceso, sobre todo cuando
esta dificultad no impide su obtención si no que simplemente provoca
freír meneame a llamadas `HTTP`.
