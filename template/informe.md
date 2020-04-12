Este informe abarca desde
[`{{min_date}}`](https://www.meneame.net/story/{{min_portada}}) a
[`{{max_date}}`](https://www.meneame.net/story/{{max_portada}}) del portal
[meneame.net](https://www.meneame.net/), lo que representa
`{{general.comments.total | millar }}` comentarios y
`{{general.links.total | millar }}` noticias repartidas en:

| Estado | Noticias         | Comentarios                       |
|--------|-----------------:|----------------------------------:|
{% for s, c in general.links.status %}
| {{s}}  | `{{c | millar}}` | `{{general.comments.status[s] | millar}}` |
{% endfor%}

O si solo atendemos a los `subs` principales ({{main_subs}}) tendremos
`{{principal.comments.total | millar }}` comentarios y
`{{principal.links.total | millar }}` noticias repartidas en:

| Estado | Noticias         | Comentarios                       |
|--------|-----------------:|----------------------------------:|
{% for s, c in principal.links.status %}
| {{s}}  | `{{c | millar}}` | `{{principal.comments.status[s] | millar}}` |
{% endfor%}
