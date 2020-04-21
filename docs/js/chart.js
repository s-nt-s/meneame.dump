function rg(a, b) {
  if (b==null) {
    b=a;
    a=0;
  }
  var r=[];
  var i;
  for (i=a;i<b;i++) r.push(i);
  return r;
}

function setGraphChart(obj, dataset) {
    if (obj.id==null) obj.id = "myChart";
    if (obj.type==null) obj.type = "bar";
    var elem = document.getElementById(obj.id)
    if (obj.destroy) {
      var ch = $(elem).data("chart");
      if (ch) {
        var hd = ch.legend.legendItems.map(function(x){
          return x.hidden;
        })
        if (hd.length>dataset.length) hd = hd.slice(1);
        else if (hd.length<dataset.length) hd.unshift(false);
        hd.forEach(function(h, i){
          dataset[i].hidden=h;
        })
        ch.destroy();
      }
    }
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
    if (obj.x_label) {
      dat.options.scales["xAxes"][0]. scaleLabel= {
        display: true,
        labelString: obj.x_label
      }
    }
    if (obj.y_label) {
      dat.options.scales["yAxes"][0]. scaleLabel= {
        display: true,
        labelString: obj.y_label
      }
    }
    var i;
    for (i=0; i<dataset.length && !dat.options.legend;i++) {
      if (dataset[i].label==null) dat.options.legend={display:false};
    }
    var myChart = new Chart(ctx, dat);
    if (obj.max_y && dataset.length>1) {
      if (obj.max_y==true) obj.max_y = myChart.scales["y-axis-0"].max;
      myChart.options.scales.yAxes[0].ticks.max = obj.max_y;
      myChart.update();
    }
    $(elem).data("chart", myChart);
    return myChart;
}

function gF(obj, key, porcentaje){
  values = obj["values"].map(function(x){return x[key]});
  if (porcentaje!=null) {
    var total = values.reduce(function(a,b){return a + b}, 0);
    var dc=Math.pow(10, porcentaje);
    values = values.map(function(x){return Math.round((x*100/total)*dc)/dc});
  }
  return values;
}
function dcd() {
  var v = arguments[0];
  var sz = (arguments.length % 2==0)?arguments.length-1:arguments.length;
  var def = sz<arguments.length?arguments[sz]:null;
  var i;
  for (i=1; i<sz; i=i+2) {
    if (v==arguments[i]) return arguments[i+1];
  }
  return def;
}

var d_color={
  "red": {
    backgroundColor: 'rgba(255, 99, 132, 0.2)',
    borderColor: 'rgba(255, 99, 132, 1)'
  },
  "blue": {
    backgroundColor: 'rgba(54, 162, 235, 0.2)',
    borderColor: 'rgba(54, 162, 235, 1)',
  }
}

function chartMensual(value) {
  var t = value || $("#tipoMensual").val();
  obj = mensual[t];
  var labels = obj["keys"].map(function(x) {return x.toFixed(2);})
  var dataset = [{
      label: "% votos negativos",
      data: gF(obj, "negatives"),
      backgroundColor: d_color.red.backgroundColor,
      borderColor: d_color.red.borderColor,
      borderWidth: 1
    },{
      label: "Karma (media)",
      data: gF(obj, "karma"),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: "orange",
      borderWidth: 1,
      hidden: true
    },/*{
      label: "% votos positivos",
      data: gF(obj, "positives"),
      backgroundColor: d_color.blue.backgroundColor,
      borderColor: d_color.blue.borderColor,
      borderWidth: 1
    },*/{
      label: "Comentarios (media)",
      data: gF(obj, "comments"),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: "green",
      borderWidth: 1,
      hidden: true
    }/*,{
      label: "Noticias",
      data: gF(obj, "noticias"),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: "black",
      borderWidth: 1,
      hidden: true
    }*/
  ];
  setGraphChart({
      id: 'data_mensual',
      title: null,
      labels: labels,
      type: 'line',
      destroy:true
  }, dataset);
}

function chartConteo(value) {
  var t = value || $("#tipoConteo").val();
  if (t=="_") t="";
  var obj = mensual["estados"];
  var dataset = [];
  var i, k, kl;
  var ks = Object.keys(obj["values"][0]);
  for (i=0; i<ks.length; i++) {
    k = ks[i];
    if (t.length>0 && !k.startsWith(t)) continue;
    if (t.length==0 && k.indexOf("_")>-1) continue;
    kl = k.substr(t.length);
    var color = dcd(kl,
      "published", "green",
      "total", "blue",
      "autodiscard", "lightsalmon",
      "discard", "red",
      "queued", "grey",
      "lightcoral"
    );
    dataset.push({
      label: kl,
      data: gF(obj, k),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: color,
      borderWidth: 1,
      hidden: kl=="autodiscard"
    })
  }
  setGraphChart({
      id: 'data_estados',
      title: null,
      labels: obj["keys"].map(function(x) {return x.toFixed(2);}),
      type: 'line',
      max_y: t=="prc_"?100:null,
      destroy:true
  }, dataset);
}

function chartDiaNormal(value) {
  var t = value || $("#tipoDiaNormal").val();
  if (t=="_") t="";
  var obj = mensual["horas"];
  var horas = rg(24);
  var years=$("#yearsDiaNormal").val();//.map(function(x){return Number(x)});
  years = years?[Number(years)]:[];
  var i,k,v,c,h;
  var values=obj["values"];
  if (years.length>0) {
    values=[];
    for (i = 0;i<obj["keys"].length;i++) {
        k = obj["keys"][i];
        if (years.indexOf(Math.floor(k))>=-1) {
          v = obj["values"][i];
          values.push(v);
       }
    }
  }
  var keys;
  var data={};
  horas.forEach(function(h){
    values.forEach(function(_v){
      if (_v[h]) {
        v = _v[h];
        if (data[h]==null) data[h]=v;
        else {
          Object.keys(v).forEach(function(k){
            data[h][k] = (data[h][k] || 0) + v[k];
          })
        }
      }
    })
  })
  data = parseObj(data);

  var labels = data["keys"].map(function(x) {
    if (x==9) return "09-10";
    if (x>9) return x+"-"+(x+1);
    return "0"+x+"-0"+(x+1);
  })
  var dataset = [{
      label: (t=="prc_"?"% ":"")+"envios",
      data: gF(data, "todas", (t=="prc_"?2:null)),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: "black",
      borderWidth: 1
    },{
      label: (t=="prc_"?"% ":"")+"published",
      data: gF(data, "published", (t=="prc_"?2:null)),
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: "green",
      borderWidth: 1
    }
  ];
  setGraphChart({
      id: 'dia_normal',
      title: null,
      labels: labels,
      type: 'line',
      destroy:true,
      //max_y: t=="prc_"?100:null,
      x_label: "Horas del día"
  }, dataset);
}


function chartCategoria(value) {
  var prc = $("#tipoCategoria").val()=="prc_";
  var portada = $("#tipoCategoriaPortada").val()=="portada";
  var obj = mensual["categorias"];
  var dataset = [];
  var i, k, kl;
  var ks = Object.keys(obj["values"][0]).filter(function(k){
    return k.startsWith("portada_")?portada:!portada;
  });
  var data_values;
  var dataset=[];
  var totales=gF(obj, portada?"portada_total":"total");
  for (i=0; i<ks.length; i++) {
    k = ks[i];
    kl = k;
    if (kl.startsWith("portada_")) kl = kl.substr(8);
    data_values=gF(obj, k);
    if (prc) {
      if (kl=="total") continue;
      data_values = data_values.map(function (cv, inx) {
          cv = cv*100/totales[inx];
          return Math.round(cv*100)/100;
      })
    }

    dataset.push({
      label: kl,
      data: data_values,
      fill: false,
      //backgroundColor: d_color.blue.backgroundColor,
      borderColor: ["black", "grey", "blue", "green", "SaddleBrown", "lightcoral", "yellow", "orange", "pink"][i] || "grey",
      borderWidth: 1,
      hidden: kl=="mnm" || kl=="otros"
    })
  }
  setGraphChart({
      id: 'data_categoria',
      title: null,
      labels: obj["keys"].map(function(x) {return x.toFixed(2);}),
      type: 'line',
      //max_y: t=="prc_"?100:null,
      destroy:true
  }, dataset);
}


$(document).ready(function(){
  chartMensual();
  chartConteo();
  chartDiaNormal();
  chartCategoria();
  $("#tipoMensual").change(function(){chartMensual(this.value)})
  $("#tipoConteo").change(function(){chartConteo(this.value)})
  $("#tipoDiaNormal").change(function(){chartDiaNormal(this.value)})
  $("#yearsDiaNormal").change(function(){chartDiaNormal()})
  $("#tipoCategoria,#tipoCategoriaPortada").change(function(){chartCategoria()})
})
