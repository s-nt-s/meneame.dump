Este informe abarca desde
[`{{min_date}}`](https://www.meneame.net/story/{{min_portada}}) a
[`{{max_date}}`](https://www.meneame.net/story/{{max_portada}}) del portal
[meneame.net](https://www.meneame.net/), lo que representa
{{comments.total | millar }} comentarios y
{{links.total | millar }} noticias repartidas en:

<table>
<thead>
  <tr>
    <th>Estado</th>
    <th>Noticias</th>
    <th>Comentarios</th>
  </tr>
</thead>
<tbody>
{% for s, c in links.status %}
<tr>
  <td>{{s}}</td>
  <td style="text-align: right;"><code>{{c | millar}}</code></td>
  <td style="text-align: right;"><code>{{comments.status[s] | millar}}</code></td>
<tr>
{% endfor%}
</tbody>
</table>
