Este informe abarca desde
[`{{min_date}}`](https://www.meneame.net/story/{{min_portada}}) a
[`{{max_date}}`](https://www.meneame.net/story/{{max_portada}}) del portal
[meneame.net](https://www.meneame.net/), lo que representa
`{{comments.total | millar }}` comentarios y
`{{links.total | millar }}` noticias repartidas en:

| Estado | Noticias         | Comentarios                       |
|--------|-----------------:|----------------------------------:|
{% for s, c in links.status %}
| {{s}}  | `{{c | millar}}` | `{{comments.status[s] | millar}}` |
{% endfor%}
