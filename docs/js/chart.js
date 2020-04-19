function setGraphChart(obj, dataset) {
    if (obj.id==null) obj.id = "myChart";
    if (obj.type==null) obj.type = "bar";
    var elem = document.getElementById(obj.id)
    var ctx = elem.getContext('2d');
    var dat = {
        type: obj.type,
        data: {
            labels: obj.labels,
            datasets: dataset
        },
        options: {
            title: {
              display: obj.title!=null,
              text: obj.title,
            },
            tooltips: {
              mode: 'index',
              intersect: false
            },
            responsive: true,
            scales: {
              xAxes: [{
                stacked: true,
              }],
              yAxes: [{
                ticks: {
                    beginAtZero: true
                }
              }]
            },
            onResize: function(ch, sz)  {
              var div = $(ch.canvas).closest("div.canvas_wrapper");
              if (div.length == 0) return;
              var max_height = $("#sidebar").height() - 300;
              if (sz.height>max_height) {
                var ratio = sz.width / sz.height;
                var max_width = max_height * ratio;
                div.css("width", max_width+"px");
              }
              else div.css("width", "");
            }
        }
    };
    var i;
    for (i=0; i<dataset.length && !dat.options.legend;i++) {
      if (dataset[i].label==null) dat.options.legend={display:false};
    }
    var myChart = new Chart(ctx, dat);
    if (dataset.length>1) {
      if (obj.max_y==null) obj.max_y = myChart.scales["y-axis-0"].max;
      myChart.options.scales.yAxes[0].ticks.max = obj.max_y;
    }
    $(elem).data("chart", myChart);
    return myChart;
}

function getNivelTxt(n) {
  if (n==1) return "muy alto";
  if (n==0) return "alto";
  if (n==-1) return "bajo"
  return "";
}
function getTargetUnidad(t, v) {
  if (v==1) {
    if (t==0) return "hectárea";
    return "incendio";
  }
  if (t==0) return "hectáreas";
  return "incendios";
}
function showResultado(html, label, descarga) {
  if (!html) html='';
  if (descarga) {
      var strAhora = getStrFecha();
      var md = html_to_md(`<h1>${label}</h1>${html}<p>Ejecuado el ${strAhora}</p>`);
      md = md.replace(/℃/g, "*").replace(/°/g, "*").replace(/\s*\(α\)/g, "").replace(/\*CC/g, "*C");
      var _md = btoa(toWin(md));
      //var _csv = btoa(toWin(csv));
      var strAhora = getPthFecha();
      html = html + `
      <p class='avoidDwn'>
        <a class="aButton" download="${descarga}_${strAhora}.txt" href="data:text/plain;base64,`+_md+`" class="button"><button>Descargar resumen (txt)</button></a>
      </p>
      `;
  }
  $("#loading").hide();
  $("#resultado .content").html(html);
  ieDownloadEvent();
  mkTableSortable($("#resultado table:has(.isSortable)"));
  var tResultado = $("#tResultado");
  tResultado.html(label || tResultado.data("default"))
  var i = $("#iResultado").show().find("i");
  if (!$("#resultado .content").is(":visible")) i.click();
  $("#limpiar").show().find("a").show();
}

function inputAnualToHtml(obj, _class) {
  if (!_class) _class='';
  var i, t, c, v;
  var zonas = obj.input.zona.map(function(k) { return TXT.zonas[k] })
  zonas = zonas.join(", ");
  var mode = obj.input.rango_temporal.join(", ")
  var evlu = obj.input.rango_temporal_evaluar?obj.input.rango_temporal_evaluar.join(", "):null;
  var pred = "";
  for (i=0;i<obj.input.check_meteo_param.length;i++) {
    c = obj.input.check_meteo_param[i]
    t = TXT.check_meteo_param[c]
    v = obj.input[c];
    pred = pred + "<li>"+t+": "+v+"</li>";
  }
  var html=`
  <h2>Datos del entrenamiento</h2>
  <ul class='${_class}'>
    <li>Región: ${zonas}</li>
    <li>Target: ${TXT.capana_verano_target[obj.input.target]}</li>
    <li>Reg. Ridge (α): ${spanNumber(obj.alpha_ridge,2)}</li>
    <li class="annos_modelo">Años modelo: ${mode}</li>
    <li>Años evaluación: ${evlu}</li>
    <li class='hide avoidMd'>Predictores:
      <ul>
        ${pred}
      </ul>
    </li>
  </ul>
  `
  html = html.replace(/^.*\bnull\b.*$/gm, "");
  return html;
}

function inputSemanalToHtml(obj, _class) {
  if (!_class) _class='';
  var i, t, c, v;
  var zonas = obj.input.zona.map(function(k) { return TXT.zonas[k] })
  zonas = zonas.join(", ");
  var mode = obj.input.rango_temporal.join(", ")
  var pred = "";
  for (i=0;i<obj.input.check_meteo_param.length;i++) {
    c = obj.input.check_meteo_param[i]
    t = TXT.check_meteo_param[c]
    if (obj.input.pred_temporalidad.indexOf(c)>-1) {
      pred = pred + "<li>"+t+" con temporalidad</li>";
    } else {
      pred = pred + "<li>"+t+"</li>";
    }
  }
  var html=`
  <h2>Datos del entrenamiento</h2>
  <ul class='${_class}'>
    <li>Región: ${zonas}</li>
    <li>Target: ${TXT.capana_verano_target[obj.input.target]}</li>
    <li>Considerar incendios previos: ${obj.input.target?'SI':'NO'}</li>
    <li class="annos_modelo">Años modelo: ${mode}</li>
    <li>Predictores:
      <ul>
        ${pred}
      </ul>
    </li>
  </ul>
  `
  html = html.replace(/^.*\bnull\b.*$/gm, "");
  return html;
}

function datoToPoints() {
  var data = arguments[0].data;

  var backgroundColor, borderColor;
  var points=[];
  var i, c, point, field;
  for (i=0; i<data.labels.length; i++) {
    point = {"label":data.labels[i]};
    for (c=1; c<arguments.length; c++) {
      field = arguments[c];
      point[field] = data.datasets[c-1].data[i];
      backgroundColor = data.datasets[c-1].backgroundColor;
      borderColor = data.datasets[c-1].borderColor;
      if (Array.isArray(backgroundColor)) point[field+"_backgroundColor"] = backgroundColor[i];
      if (Array.isArray(borderColor)) point[field+"_borderColor"] = borderColor[i];
    }
    points.push(point)
  }
  return points;
}

function pointToData(points) {
  var data={}
  var k, i, p;
  for (k in points[0]) data[k]=[];
  for (i=0;i<points.length;i++) {
    p=points[i];
    for (k in p) {
      data[k].push(p[k]);
    }
  }
  return data;
}

function reorderVeranoChart(btn) {
  btn = $(btn);
  var defTxt = btn.data("deftxt");
  if (!defTxt) {
    defTxt = btn.text().trim()
    btn.data("deftxt", defTxt);
  }
  btn.prop("disabled", true);
  var myChart = $("#myChart").data("chart");
  var _text = null;
  var _ordr = btn.data("order");
  if (_ordr) {
    _text = "Ordenar por año";
    _ordr = myChart.options.data_order[_ordr];
  } else {
    _text = defTxt;
    _ordr = myChart.options.data_order[_ordr];
  }
  var dt;
  var index=0;
  myChart.data.labels = _ordr.label;
  if (_ordr.predi) {
    dt = myChart.data.datasets[index++]
    dt.data = _ordr.predi;
    if (_ordr.predi_backgroundColor) dt.backgroundColor = _ordr.predi_backgroundColor;
    if (_ordr.predi_borderColor) dt.borderColor = _ordr.predi_borderColor;
  }
  if (_ordr.varel) {
    dt = myChart.data.datasets[index++]
    dt.data = _ordr.varel;
    if (_ordr.varel_backgroundColor) dt.backgroundColor = _ordr.varel_backgroundColor;
    if (_ordr.varel_borderColor) dt.borderColor = _ordr.varel_borderColor;
  }
  myChart.update();
  btn.text(_text);
  btn.data("order", (btn.data("order") + 1) % 2);
  btn.prop("disabled", false);
}

$(document).ready(function() {
  $("button[name='set_meteo_param_val']").click(function(){
    var t=$(this).closest("form");
    var z=t.find("select[name='zona[]']").val();
    var isSpain=(z.length==1)?(z[0]=="ESP"):false;
    var obj={}
    var v, k;
    for (const [key, value] of Object.entries(meta_info["ultimo_meteo"])) {
      if (isSpain || z.includes(key)) {
        for (const [prm, val] of Object.entries(value)) {
          v = obj[prm] || [];
          v.push(val);
          obj[prm] = v;
        }
      }
    }
    var _getSum = function getSum(total, num) {return total + num;}
    for (const [key, value] of Object.entries(obj)) {
      k = PARAMS_SERVER_CLIENT[key] || key;
      v = value.reduce(_getSum, 0) / value.length;
      v = Math.round(v*100)/100;
      obj[k] = v;
    }
    t.find(".meteo_predictores input[type=number]").each(function(){
      var e=$(this);
      var v = obj[e.attr("name")];
      if (v!=null) e.val(v);
    })
  });

  $("button.set_meteo_param_val_prediccion_semanal").click(function(){
    var t=$(this).closest("form");
    var z=t.find("select[name='predictor_zona']").val();
    var p_semanal = prediccion_semanal[z];
    var p_ultimo = meta_info["ultimo_meteo"][z];
    t = $(this).closest(".meteo_predictores");
    t.find("input[type=number]").each(function(){
      var v = null;
      var n = this.name.split(/_\d+_/);
      n = n[n.length-1];
      if (n == "prim_tmed" || n == "prin_prec") {
        v = p_ultimo[PARAMS_CLIENT_SERVER[n]];
      } else {
        v = p_semanal[n];
      }
      this.value=v==null?"":Math.round(v*100)/100;;
    });
  });


  $("select[name='predecir_o_analizar']").change(function(){
    if (!this.value) return;
    var t = $(this);
    var predi = t.find_in_parents(".meteo_predictores");
    var annos = t.find_in_parents("select[name='rango_temporal[]']");
    predi.removeClass("meteo_predictores_a meteo_predictores_p")
    predi.addClass("meteo_predictores_"+this.value);
    if (this.value == "a") {
      annos.data("min", 10);
      predi.find("input[type='number']").prop("required", false);
    }
    else if (this.value == "p") {
      annos.data("min", 3);
      predi.find("input[type='number']").prop("required", true);
    }
    annos.change();
  }).change()
  $("#prediccion-modelo-semana-provincia select[name='zona[]']").change(function() {
    var slc = $("#prediccion-modelo-semana-provincia .predictor_zona");
    var val = slc.val()
    slc.find("option").show();
    var vals = $(this).val();
    if (vals.indexOf("ESP")==-1) {
      slc.find("option").filter(function(){return this.value && vals.indexOf(this.value)==-1}).hide();
      if (vals.indexOf(val)==-1) {
        slc.val("").change();
      }
    }
  }).change();
  $("input[name=ventana_size]").change(function(){
    var t=$(this);
    var v=parseInt(t.val(), 10);
    if (isNaN(v)) return;
    var c=t.closest("fieldset").find("input[name=incendios_previos]");
    c.prop("disabled", v==0);
    t.closest("form").find("fieldset.meteo_predictores .con_temporalidad")[v==0?"hide":"show"]();
    if (v==0) c.prop("checked", false);
    c.add(c.getLabel()).css("opacity", v==0?0.5:'');
  }).change();
});



ON_ENDPOINT["analisis_anual"]=function(data, textStatus, jqXHR) {
    var obj = data;//.status?objForm(form):data;
    if (textStatus!="success") return false;

    var i, c, p, table, cels, v;
    var html="";

    html = html + `
      <h2>Error absoluto</h2>
      <ul class='big dosEnteros dosDecimales'>
        <li title='Error medio  de los valores reales respecto al valor medio'><b>Baseline</b>: <code>${spanNumber(obj.baseline, 2)}</code> ${getTargetUnidad(obj.input.target, obj.baseline).toCapitalize()}</li>
        <li title='Error medio de los valores reales respecto a las predicciones'><b>Error medio</b>: <code>${spanNumber(obj.mae, 2)}</code> ${getTargetUnidad(obj.input.target, obj.mae).toCapitalize()}</li>
        <li title='Porcentaje explicado por el modelo'><b>Carga explicativa</b>: <code>${spanNumber(obj.cargaexplicativa, 2)}%</code> </li>
      </ul>
    `;
    if (obj.pvalor != null) {
    html = html + `
      <h2>Acierto relativo</h2>
      <ul class='big dosEnteros'>
        <li title='Valor de correlación entre valor real y predicción para los años evaluados'><code>${spanNumber(obj.spearman*100, 0)}%</code> <b>spearman</b></li>
        <li title='Valor de significancia de la correlación de Spearman'><code>${spanNumber(obj.pvalor, 2)}</code> <b>p-valor</b></li>
        <li title=''>Nivel de significancia ${getNivelTxt(obj.nivel_significativo)}</li>
      </ul>
    `;
    }

    html = html + "<h2>Predicción vs realidad</h2>"

    cels = [
      {"class": "isSortable isSortedByMe", "txt":"Año"},
      {"class": "isSortable", "txt":"Predicción"},
      {"class": "isSortable", "txt":"Valor real"}
    ];
    var prediccion=[];
    var valor_real=[];
    for (i=0; i<obj.annos.length; i++) {
      p = Math.round(obj.prediccion[i]*100)/100
      v = Math.round(obj.valor_real[i]*100)/100;
      prediccion.push(p);
      valor_real.push(v);
      cels.push(obj.annos[i]);
      cels.push(`<code>${spanNumber(obj.prediccion[i], 2)}</code>`);
      cels.push(`<code>${spanNumber(obj.valor_real[i], 2)}</code>`);
    }

    table = buildTable("numbers"+(obj.input.target==0?" dosDecimales":""), 3, cels);
    table = table.replace("<thead>", "<thead><tr><th></th><th colspan='2' style='text-align: center;'>"+getTargetUnidad(obj.input.target).toCapitalize()+"</th></tr>");
    html = html + table + `
      <div class="canvas_wrapper">
        <canvas id="myChart"></canvas>
      </div>
      <button onclick="reorderVeranoChart(this)" data-order="1">Ordenar por valor real</button>
    `;

    cels = [
      {"class":"txt", "txt": "Predictor"}
    ];
    for (i=0; i<obj.annos.length; i++) {
      cels.push(obj.annos[i])
    }
    var row_size = cels.length;
    for (c=0; c<obj.predictores.length;c++) {
      p = obj.predictores[c];
      cels.push(TXT.check_meteo_param[p]);
      for (i=0; i<obj.annos.length; i++) {
        cels.push(`<code>${spanNumber(obj.coeficientes[i][c], 2)}</code>`);
      }
    }
    table = buildTable("numbers dosDecimales tableScroll", row_size, cels);
    table = table.replace("<thead>", "<thead><tr><th colspan='1'></th><th colspan='"+(obj.annos.length)+"' style='text-align: center;'>Coeficiente</th></tr>");
    html = html + table;

    html = html + inputAnualToHtml(obj, "analisis")

    showResultado(html, "Resultado análisis <abbr title='campaña'>c.</abbr> verano", "analisis");

    var myChart = setGraphChart({
          id: 'myChart',
          title: getTargetUnidad(obj.input.target).toCapitalize(),
          labels: obj.annos
      }, [{
          label: "Predicción",
          data: prediccion,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
      },{
          label: "Valor real",
          data: valor_real,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
    }]);
    var points = datoToPoints(myChart, "predi", "varel");
    myChart.options.data_order = [
      pointToData(points.sort(function(a, b) {return a.label - b.label;})),
      pointToData(points.sort(function(a, b) {
        var x = a.varel - b.varel;
        if (x!=0) return -x;
        return a.label - b.label;
      }))
    ]
    return true
}
ON_ENDPOINT["prediccion_anual"]=function(data, textStatus, jqXHR) {
    var obj = data;//.status?objForm(form):data;
    if (textStatus!="success") return false;

    var cels = null;
    var html="";

    html = html + `
      <p><strong>Predicción:</strong> ${spanNumber(obj.prediccion, 0)} ${getTargetUnidad(obj.input.target, obj.prediccion)}</p>
    `;
    cels = [
      {"class":"txt", "txt": "Predictor"}, "Valor usado", "Coeficiente"
    ];
    for (var [key, value] of Object.entries(obj.coeficientes)) {
      cels.push(TXT.check_meteo_param[key]);
      cels.push(`<code>${obj.input[key]}</code> <span class='unidades'>${TXT.unidad[key]}</span>`);
      cels.push(`<code>${spanNumber(value, 2)}</code>`);
    }
    html = html + buildTable("numbers dosDecimales", 3, cels) + `
      <div class="canvas_wrapper">
        <canvas id="myChart"></canvas>
      </div>
      <button onclick="reorderVeranoChart(this)" data-order="1">Ordenar por ${getTargetUnidad(obj.input.target)}</button>
    `;

    html = html + inputAnualToHtml(obj, "prediccion");

    html = html + "<p>Años del modelo y "+(obj.input.target==0?"las hectareas quemadas":"el número de incendios")+" en dicho año:</p>";

    cels = [
      {"class": "isSortable isSortedByMe", "txt":"Año"},
      {"class": "isSortable", "txt":getTargetUnidad(obj.input.target).toCapitalize()}
    ]
    var annos=[];
    var valre=[];
    var backgroundColor=[];
    var borderColor=[];
    for (var [key, value] of Object.entries(obj.valor_real)) {
      annos.push(key);
      valre.push(Math.round(value*100)/100);
      cels.push(key);
      cels.push(`<code>${spanNumber(value, 2)}</code>`);
      backgroundColor.push('rgba(54, 162, 235, 0.2)');
      borderColor.push('rgba(54, 162, 235, 1)');
    }
    annos.push("predicción");
    valre.push(Math.round(obj.prediccion*100)/100);
    backgroundColor.push('rgba(255, 99, 132, 0.2)');
    borderColor.push('rgba(255, 99, 132, 1)');
    html = html + buildTable("numbers dosDecimales", 2, cels);

    showResultado(html, "Resultado predicción <abbr title='campaña'>c.</abbr> verano", "prediccion");

    var myChart = setGraphChart({
        id: 'myChart',
        title: getTargetUnidad(obj.input.target).toCapitalize(),
        labels: annos
    }, [{
        label: null,
        data: valre,
        backgroundColor: backgroundColor,
        borderColor: borderColor,
        borderWidth: 1
    }]);
    var points = datoToPoints(myChart, "varel");
    myChart.options.data_order = [
      pointToData(points.sort(function(a, b) {return a.label - b.label;})),
      pointToData(points.sort(function(a, b) {
        var x = a.varel - b.varel;
        if (x!=0) return -x;
        return a.label - b.label;
      }))
    ]
    return true;
}

ON_ENDPOINT["prediccion_semana_provincia"]=function(data, textStatus, jqXHR) {
  var obj = data;//.status?objForm(form):data;
  if (textStatus!="success") return false;
  var html = "";
  var isVr = obj.input.semana!=null && obj.semana_prevision!=null;
  if (isVr) {
    var smn = obj.semana_prevision.toFixed(2).replace(".","-W");
    var title='';
    if (smn!=obj.input.semana) {
      title=` title='La semana ${obj.input.semana} no esta disponible así que se usara la semana ${smn}'`
      smn = smn + ` <strike>${obj.input.semana}</strike>`;
    }
    html = html + `
    <ul class="dosEnteros">
      <li${title}><b>Semana</b>: ${smn}</li>
      <li title='Error medio de los valores reales respecto a las predicciones'><b>Error medio</b>: <code>${spanNumber(obj.mae, 2)}</code> ${getTargetUnidad(obj.input.target, obj.mae)}</li>
      <li title='Valor de correlación entre valor real y predicción para los años evaluados'><b>Spearman:</b> <code>${spanNumber(obj.spearman*100, 0)}%</code></li>
    `
  } else if (obj.input.semana_actual) {
    var y = obj.input.semana_actual.split("-W");
    var s = Number(y[1]);
    var y = Number(y[0]);
    html = html + `
    <ul>
      <li><b>Semana</b>: <span title="Semana ${s}ª del año ${y}">${obj.input.semana_actual}</span></li>
    `
  } else {
    html = html + `<ul>`
  }
  if (obj.input.ventana_size==obj.ventana_size) {
    html = html + `<li><b>Tamaño de ventana</b>: ${obj.input.ventana_size}</li>`;
  } else {
    html = html + `<li><b>Tamaño de ventana</b>: Se solicitó ${obj.input.ventana_size}, pero se ha usado ${obj.ventana_size} por falta de datos</li>`;
  }

  if (obj.input.incendios_previos==null || obj.input.incendios_previos==0) {
    html = html + `<li><b>Considerar incendios previos</b>: NO</li>`;
  } else {
    html = html + `<li><b>Considerar incendios previos</b>: `;
    if (obj.temporalidad_off == false) {
      html = html + `SI</li>`;
    } else if (obj.temporalidad_off == true) {
      html = html + `Se solicitó, pero ha tenido que ser desactivado por no disponer de datos suficientes</li>`;
    } else {
      if (obj.temporalidad_off.length==1) {
        var z=obj.temporalidad_off[0];
        z = TXT.zonas[z];
        html = html + `SI, menos en ${z} por falta de datos</li>`;
      } else {
        html = html + `SI, menos en: <ul>`;
        var i,k;
        for (i=0; i<obj.temporalidad_off.length;i++) {
          k = obj.temporalidad_off[i];
          html = html + `<li>${TXT.zonas[k]}</li>`;
        }
        html = html + `</ul> por falta de datos</li>`;
      }
    }
  }
  html = html + `</ul>`;

  var cels=[
    {"class":"txt isSortable", "txt": "Provincia"},
    {"class":"isSortable", "txt": getTargetUnidad(obj.input.target).toCapitalize()}
  ]
  if (isVr && obj.valor_real) {
    cels[cels.length-1].txt="Predicción"
    cels.push({"class":"isSortable", "txt": "Valor real"});
  }

  for (var [key, value] of Object.entries(obj.prediccion)) {
    cels.push(TXT.zonas[key]);
    cels.push(`<code>${spanNumber(value, obj.input.target==0?2:0)}</code>`);
    if (isVr && obj.valor_real) {
      var v=obj.valor_real[key];
      if (v==null) cels.push("");
      else cels.push(`<code>${spanNumber(v, obj.input.target==0?2:0)}</code>`);
    }
  }
  table = buildTable("numbers greycero "+(obj.input.target==0?"dosDecimales":""), (isVr && obj.valor_real)?3:2, cels);
  html = html + table;

  if (isVr && obj.valor_real) {
    html = html.replace("<thead>","<thead><tr><th></th><th colspan='2' style='text-align:center'>"+getTargetUnidad(obj.input.target).toCapitalize()+"</th>");
  } else {
    html = html + `
      <p class="avoidMd show_hide_cero">
        <input type='checkbox' onclick="$('tr.is_cero').toggleClass('hide')" id='show_hide_cero'>
        <label for='show_hide_cero'>
          Mostrar provincias con predicción igual a <code>0</code>
        </label>
      </p>
    `
  }

  showResultado(html, "Resultado predicción semanal", "prediccion");

  var trs = $("#resultado .content table tbody tr");
  if (trs.length<2) {
    $("p.show_hide_cero").remove();
  } else {
    if (!(isVr && obj.valor_real)) {
      var trs = trs.filter(":has(span.sig_cero)")
      if (trs.length) {
        trs.addClass("is_cero").addClass("hide");
      } else {
        $("p.show_hide_cero").remove();
      }
    }
  }

  var values = Object.entries(obj.prediccion).map(function(k){return k[1]});
  var fls = getFieldSetRangos({
    title:"Personalizar mapa",
    class: "prediccion_semana_provincia_rangos"+(obj.input.target==0?" dosDecimales":""),
    pre: "<p>Use este panel para personalizar como se muestra la información en el mapa.</p>",
    min: 0,
    add: obj.input.target==0?0.01:1,
    decimales: obj.input.target==0?2:0,
    values: values,
    rangos: ["Verde", "Amarillo", "Rojo"],
    unidades: getTargetUnidad(obj.input.target),
    prediccion: obj.prediccion,
    decimales: obj.input.target==0?2:0,
    globalchange: function(event, rng){
      var i, r, a, b, c, v;
      var t = $(this);
      var obj = t.data("range_config");
      var prov_color={};
      if (t.is(".plan_b")) {
        for (var [key, value] of Object.entries(obj.prediccion)) {
          prov_color[key]=rng[value];
        }
      } else {
        for (var [key, value] of Object.entries(obj.prediccion)) {
          var flag = true;
          for (i=0;!(key in prov_color) && i<rng.length;i++) {
            r = rng[i];
            if (r!=null && value>r) continue;
            if (i==0) {
              prov_color[key]=i;
            }
            else {
              if (value>rng[i-1]) {
                  prov_color[key]=i;
              }
            }
          }
          if (!(key in prov_color)) prov_color[key]=rng.length;
        }
      }
      var str_prov_color = JSON.stringify(prov_color);
      var t = $(this);
      if (t.data("prov_color")==str_prov_color) return;

      clearMap();
      layers.prediccion_semana_provincia = L.geoJSON(geoprovincias, {
          style: function(f, l) {
            var fp = f.properties;
            var gp = f.geometry.properties;
            var v=prov_color[gp.i];
            var color="red";
            if (v==0) {
                color="green"
            } else if (v==1) {
                color="yellow"
            }
            return {
              "color": color,
              "weight": 5,
              "opacity": 0.10,
              "fillOpacity": 0.4
            }
          },
          onEachFeature: function(f, l) {
            var val = obj.prediccion[f.properties.i];
            var d = Math.pow(10, obj.decimales)
            val = Math.round(val*d)/d;
            val = val+" "+obj.unidades;
            l.bindTooltip(f.properties.n+"<br/>"+val);
          },
          filter: function(f, layer) {
            var fp = f.properties;
            return fp.i in prov_color;
          }
        }
      );
      layers.prediccion_semana_provincia.on({
        mouseover: function(e) {
          e.layer.setStyle({opacity: 1});
        },
        mouseout: function(e) {
          layers.prediccion_semana_provincia.resetStyle(e.layer);
        }
      });
      mymap.addLayer(layers.prediccion_semana_provincia);

      t.data("prov_color", str_prov_color);
    }
  });
  if (fls) {
    $("#resultado .content").append(fls);
  }

  return true;
}


ON_ENDPOINT["analisis_semana_provincia"]=function(data, textStatus, jqXHR) {
    var obj = data;//.status?objForm(form):data;
    if (textStatus!="success") return false;
    var i, v;

    obj.input.check_meteo_param = obj.modelo._predictores
    obj.input.pred_temporalidad = obj.modelo._temp_pred
    obj.input.rango_temporal = obj.modelo._anios_entrenmt
    obj.input.ventana_size = obj.modelo._tam_ventana

    var html =""

    html = html + `
      <h2>Valores medios</h2>
      <ul class='big dosEnteros dosDecimales'>
        <li title='Error medio  de los valores reales respecto al valor medio'><b>Baseline</b>: <code>${spanNumber(obj.media.baseline, 2)}</code> ${getTargetUnidad(obj.input.target, obj.baseline).toCapitalize()}</li>
        <li title='Error medio de los valores reales respecto a las predicciones'><b>Error medio</b>: <code>${spanNumber(obj.media.mae, 2)}</code> ${getTargetUnidad(obj.input.target, obj.mae).toCapitalize()}</li>
        <li title='Porcentaje explicado por el modelo'><b>Carga explicativa</b>: <code>${spanNumber(obj.media.cargaexplicativa, 2)}%</code> </li>
        <li title='Valor de correlación entre valor real y predicción para los años evaluados'><b>Spearman</b>: <code>${spanNumber(obj.media.spearman, 0)}%</code></li>
      </ul>
    `;

    html = html + `
      <h2>Detalle por año evaluado</h2>
    `;
    var annos = [];
    var cargaexplicativa = [];
    var spearman = [];
    var cels = [
      {"class": "isSortable isSortedByMe", "txt":"Año"},
      {"class": "isSortable"+(obj.input.target==0?" dosDecimales":""), "txt": "Baseline", "title": "Error medio  de los valores reales respecto al valor medio"},
      {"class": "isSortable"+(obj.input.target==0?" dosDecimales":""), "txt": "MAE", "title":"Error medio de los valores reales respecto a las predicciones"},
      {"class": "isSortable dosDecimales", "txt":"C. exp", "title": "Carga explicativa. Porcentaje explicado por el modelo"},
      {"class": "isSortable dosDecimales", "txt":"Spearman", "title":'Valor de correlación entre valor real y predicción para los años evaluados'}
    ];
    for (i=0; i<obj.input.rango_temporal_evaluar.length; i++) {
      key = Number(obj.input.rango_temporal_evaluar[i]);
      if (isNaN(key)) continue;
      cels.push(key);
      v = obj[key];
      if (v!=null) {
        annos.push(key)
        cargaexplicativa.push(Math.round(v.cargaexplicativa*100)/100);
        spearman.push(Math.round(v.spearman*100)/100);
        cels.push(spanNumber(v.baseline, obj.input.target==0?2:0));
        cels.push(spanNumber(v.mae, obj.input.target==0?2:0));
        cels.push(spanNumber(v.cargaexplicativa, 2));
        cels.push(spanNumber(v.spearman, 2));
      } else {
        cels.push({"colspan": 4, "txt": "No se disponen de datos suficientes", "style":'text-align: center;'})
      }
    }

    table = buildTable("numbers", 5, cels);
    table = table.replace("<thead>", `
      <thead>
      <tr>
        <th colspan='1'></th>
        <th colspan='2' style='text-align: center;'>${getTargetUnidad(obj.input.target).toCapitalize()}</th>
        <th colspan='2' style='text-align: center;'>Porcentaje (%)</th>
      </tr>
    `);
    table = table.replace("</tbody>", `
      </tbody>
      <tfoot>
      <tr>
        <th colspan='1'></th>
        <th colspan='3' style='text-align: center;' title='Métrica obtenida sobre las diferencias absolutas entre valores reales y predicciones'>M. absoluta</th>
        <th colspan='1' style='text-align: center;' title='Métrica obtenida sobre incidencia relativa en provincias y semanas'>M. relativa</th>
      </tr>
      </tfoot>
    `);

    html = html + table + `
      <div class="canvas_wrapper">
        <canvas id="myChart"></canvas>
      </div>
    `

    html = html + inputSemanalToHtml(obj, "analisis_semana_provincia");

    showResultado(html, "Resultado análisis semanal", "analisis");

    var myChart = setGraphChart({
          id: 'myChart',
          title: "Porcentaje (%)",
          labels: annos,
          type: "line",
          max_y: 100
      }, [{
          label: "Carga explicativa",
          data: cargaexplicativa,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
      },{
          label: "Spearman",
          data: spearman,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
    }], 100);
    /*
    var points = datoToPoints(myChart, "cargaexplicativa", "spearman");
    myChart.options.data_order = [
      pointToData(points.sort(function(a, b) {return a.label - b.label;})),
      pointToData(points.sort(function(a, b) {
        var x = a.varel - b.varel;
        if (x!=0) return -x;
        return a.label - b.label;
      }))
    ]*/

    return true;
}
