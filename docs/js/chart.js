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

function setGraphChart(obj, dataset) {
    if (obj.id==null) obj.id = "myChart";
    if (obj.type==null) obj.type = "bar";
    var elem = (typeof obj.id == "string")?document.getElementById(obj.id):obj.id;
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

function render_chart() {
  var t=$(this);
  var key_modelo = t.data("modelo") || t.find("*[name=modelo]").val();
  var mdl = modelos[key_modelo];
  if (mdl==null) {
    console.log(key_modelo+" no encontrado");
    return;
  }
  var prc = t.find("*[name=porcentaje]").val()=="1";
  if (prc && t.data("porcentaje")!="0") {
    var _mdl = {
      "keys": mdl["keys"].slice(),
      "values": []
    }
    mdl["values"].forEach(function(v){
      var total = v["total"];
      if (total==null) total = Object.values(v).reduce(function(a,b){return a + b}, 0)
      var nv={};
      Object.entries(v).forEach(([key, value]) => {
        if (key!="total") {
          nv[key]=value*100/total;
          nv[key]=Math.round(nv[key]*100)/100;
        }
      });
      _mdl["values"].push(nv);
    });
    mdl=_mdl;
  }
  var rd = render_builder[key_modelo];
  if (rd==null) {
    console.log(key_modelo+" no encontrado builder");
    return;
  }
  rd.apply(t, [mdl, prc]);
}

$(document).ready(function(){
  $("div.data")
  .on("render", render_chart)
  .find("select").change(function(){
    $(this).closest("div.data").trigger("render");
  });
  $("div.data").trigger("render");
  /*
  return;
  chartMensual();
  chartConteo();
  chartDiaNormal();
  chartCategoria();
  $("#tipoMensual").change(function(){chartMensual(this.value)})
  $("#tipoConteo").change(function(){chartConteo(this.value)})
  $("#tipoDiaNormal").change(function(){chartDiaNormal(this.value)})
  $("#yearsDiaNormal").change(function(){chartDiaNormal()})
  $("#tipoCategoria,#tipoCategoriaPortada").change(function(){chartCategoria()})
  */
})

render_builder={
  "horas_dia":function(obj, prc) {
      var horas = rg(24);
      var year=parseInt($("#yearsDiaNormal").val(), 10);//.map(function(x){return Number(x)});
      if (isNaN(year)) year=null;
      var divisor = 365*(year?1:($("#yearsDiaNormal option").length-1));
      var i,k,v,c,h;
      var values=obj["values"];
      if (year) {
        values=[];
        for (i = 0;i<obj["keys"].length;i++) {
            k = obj["keys"][i];
            if (k==year) {
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
      var td = gF(data, "todas", (prc?2:null));
      var pb = gF(data, "published", (prc?2:null));
      if (!prc) {
        var rnd=function(x) {
          var a=x/divisor;
          var b=Math.round(a);
          return b==0 && a!=0?(Math.round(a*10)/10):b;
        }
        td = td.map(rnd);
        pb = pb.map(rnd);
      }
      var dataset = [{
          label: (prc?"% ":"")+"envios",
          data: td,
          fill: false,
          //backgroundColor: d_color.blue.backgroundColor,
          borderColor: "black",
          borderWidth: 1
        },{
          label: (prc?"% ":"")+"published",
          data: pb,
          fill: false,
          //backgroundColor: d_color.blue.backgroundColor,
          borderColor: "green",
          borderWidth: 1
        }
      ];
      setGraphChart({
          id: this.find("canvas")[0],
          title: null,
          labels: labels,
          type: 'line',
          destroy:true,
          //max_y: t=="prc_"?100:null,
          x_label: "Horas del día"
      }, dataset);
  },
  "count_estados":function(obj, prc) {
    var dataset = [];
    var i, k, kl;
    var ks = Object.keys(obj["values"][0]);
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      var color = dcd(k,
        "published", "green",
        "total", "blue",
        "autodiscard", "lightsalmon",
        "discard", "red",
        "queued", "grey",
        "lightcoral"
      );
      dataset.push({
        label: k,
        data: gF(obj, k),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: color,
        borderWidth: 1,
        hidden: k=="autodiscard"
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"].map(function(x) {return x.toFixed(2);}),
        type: 'line',
        max_y: prc?100:null,
        destroy:true
    }, dataset);
  },
  "count_categorias_todas": function(obj, prc) {
    var dataset = [];
    var i, k, kl;
    var ks = Object.keys(obj["values"][0]);
    var colors = ["black", "grey", "blue", "green", "SaddleBrown", "lightcoral", "yellow", "orange", "pink"];
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      dataset.push({
        label: k,
        data: gF(obj, k),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: colors.slice(prc?1:0)[i] || "grey",
        borderWidth: 1,
        hidden: k=="mnm" || k=="otros"
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"].map(function(x) {return x.toFixed(2);}),
        type: 'line',
        //max_y: t=="prc_"?100:null,
        destroy:true
    }, dataset);
  },
  "misce_general": function (obj, prc) {
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
        id: this.find("canvas")[0],
        title: null,
        labels: labels,
        type: 'line',
        destroy:true
    }, dataset);
  }
}
render_builder["count_categorias_published"] = render_builder["count_categorias_todas"];
render_builder["misce_general"] = render_builder["misce_general"];
render_builder["misce_portada"] = render_builder["misce_general"];
render_builder["misce_actualidad"] = render_builder["misce_general"];
