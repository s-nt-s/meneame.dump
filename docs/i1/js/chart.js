var DFL_COLOR = [
  "black", "blue", "green", "SaddleBrown", "Purple", "Lime", "lightcoral", "orange", "Aqua", "Fuchsia", "yellow"
];
Chart.defaults.LineWithLine = Chart.defaults.line;
Chart.controllers.LineWithLine = Chart.controllers.line.extend({
   draw: function(ease) {
      Chart.controllers.line.prototype.draw.call(this, ease);

      if (this.chart.tooltip._active && this.chart.tooltip._active.length) {
         var activePoint = this.chart.tooltip._active[0],
             ctx = this.chart.ctx,
             x = activePoint.tooltipPosition().x,
             topY = this.chart.legend.bottom,
             bottomY = this.chart.chartArea.bottom;

         // draw line
         ctx.save();
         ctx.beginPath();
         ctx.moveTo(x, topY);
         ctx.lineTo(x, bottomY);
         ctx.lineWidth = 0.5;
         ctx.strokeStyle = '#07C';
         ctx.stroke();
         ctx.restore();
      }
   }
});

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
      var $elem = $(elem);
      var ch = $elem.data("chart");
      if (ch) {
        var hd = $elem.data("full_hidden") || {};
        ch.legend.legendItems.forEach(function(x){
          return hd[x.text]=x.hidden;
        })
        dataset.forEach(function(d, i){
          d.hidden=hd[d.label]==null?d.hidden:hd[d.label];
          hd[d.label]=d.hidden;
        })
        $elem.data("full_hidden", hd);
        ch.destroy();
      }
    }
    if (obj.labels.length && typeof obj.labels[0] == "number"){
      var dc = obj.labels.reduce(function(a,b){
        return Math.max(
          a,
          Math.floor(b) == b?0:b.toString().split(".")[1].length,
        )
      }, 0);
      obj.labels = obj.labels.map(function(x) {return x.toFixed(dc);})
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
              //mode: 'nearest',
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
    if (obj.porcentaje) {
      dat.options.scales.yAxes[0].ticks.callback=function(value, index, values) {
          return value+' %';
      }
    }
    dat.data.datasets.forEach(function(i){
      if (!i.pointBackgroundColor) i.pointBackgroundColor=i.borderColor;
      if (!i.pointBorderColor) i.pointBorderColor=i.borderColor;
    });
    if (!obj.show_points) {
        if (!dat.options.hover) dat.options.hover={};
        dat.options.hover= {
          intersect: false,
          animationDuration: 0
        };
        dat.data.datasets.forEach(function(i){
          i.pointHoverRadius=3;//i.pointRadius;
          i.pointRadius = 0;
        });
    }
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
  values = obj["values"].map(function(x){return x[key] || 0});
  if (porcentaje!=null) {
    var total = values.reduce(function(a,b){return a + b}, 0);
    var dc=Math.pow(10, porcentaje);
    values = values.map(function(x){return Math.round((x*100/total)*dc)/dc});
  }
  return values;
}

function mesTo(ym) {
  var y=Math.floor(ym);
  var m=(ym*100)-(y*100);
  var obj={
    year:y,
    mes:m,
    trimestre: dcd(m,
      1,1,2,1,3,1,
      4,2,5,2,6,2,
      7,3,8,3,9,3,
      4
    ),
    cuatrimestre: dcd(m,
      1,1,2,1,3,1,4,1,
      5,2,6,2,7,2,8,2,
      3
    ),
    semestre: m<7?1:2
  }
  return obj;
}

function doAgrupar(tipo, keys) {
  var letter = tipo[0].toUpperCase();
  var re_index={}
  var last_piece=null;
  var new_keys=[]
  keys.forEach(function(item, i) {
    var lst = new_keys.length-1;
    var dt_mes = mesTo(item);
    var m = dt_mes.mes;
    if (lst==-1) {
      if (letter=="T" && !(m==1 || m==4 || m==7 || m==10)) return;
      if (letter=="C" && !(m==1 || m==5 || m==9)) return;
      if (letter=="S" && !(m==1 || m==6)) return;
      if (letter=="Y" && !(m==1)) return;
    }
    var t=dt_mes.year;
    if (letter!="Y") {
      t = t + (dt_mes[tipo]/100);
    }
    if (lst>=0 && new_keys[lst]==t) {
      re_index[i]=lst;
    } else {
      new_keys.push(t);
      re_index[i]=lst+1;
    }
    if (m==6 || m==12) last_piece=new_keys.length;
    if (letter=="T" && (m==3 || m==6 || m==9 || m==12)) last_piece=new_keys.length;
    if (letter=="C" && (m==4 || m==8 || m==12)) last_piece=new_keys.length;
    if (letter=="S" && (m==6 || m==12)) last_piece=new_keys.length;
  })
  new_keys=new_keys.slice(0, last_piece);
  if (letter!="Y") new_keys = new_keys.map(function(a) {return a.toFixed(2).replace(".0", " "+letter)})
  return {
    "keys": new_keys,
    "index": re_index
  }
}

function render_chart() {
  var t=$(this);
  var key_modelo = t.data("modelo") || t.find("*[name=modelo]").val();
  var mdl = modelos[key_modelo];
  if (mdl==null) {
    console.log(key_modelo+" no encontrado");
    return;
  }
  var tags = t.find(".tag_filter:not(.tagify)").data("mytagify");
  if (tags) {
    tags = tags.value.filter(function(x){
      return x.__isValid;
    }).map(function(x) {
      return x.value;
    });
  }
  var prc = t.find("*[name=porcentaje]").val()=="1";
  var agrupar = t.find("*[name=agrupar]").val();
  if (agrupar && agrupar!="mes") {
    var agr = doAgrupar(agrupar, mdl["keys"]);
    var _mdl = {
      "keys": agr.keys,
      "values": []
    }
    mdl["values"].forEach(function(v, i){
      var new_index = agr.index[i];
      if (new_index==null || new_index>=_mdl["keys"].length) return;
      var new_value = _mdl["values"][new_index];
      if (new_value==null) {
        var x = {}
        Object.assign(x, v)
        _mdl["values"].push(x);
      } else {
        Object.entries(v).forEach(([key, value]) => {
            new_value[key]=(new_value[key] || 0)+value;
        });
        _mdl["values"][new_index]=new_value;
      }
    });
    mdl=_mdl;
  }
  if (prc && t.data("porcentaje")!="0" && mdl["keys"] && mdl["values"]) {
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
  rd.apply(t, [mdl, {
    "porcentaje": prc,
    "agrupar": agrupar,
    "tags": tags,
    "jq": t
  }]);
}

$(document).ready(function(){
  $("div.data")
  .on("render", render_chart)
  .find("select,input").change(function(){
    $(this).closest("div.data").trigger("render");
  });
  $("div.data").trigger("render");
})

render_builder={
  "uso_tiempo":function(obj, options) {
      var i,k,kl,v,c,h;
      var tipo = $("#tipoCuando").val();
      var xaxis={};
      if (tipo=="dia") {
        var horas = rg(24);
        xaxis.label="Horas del día";
        xaxis.divisor = 365;
        xaxis.vals = {
          "keys": horas.map(function(x){return "H"+x}),
          "legend": horas.map(function(x) {
            if (x==9) return "09-10";
            if (x>9) return x+"-"+(x+1);
            return "0"+x+"-0"+(x+1);
          })
        }
      } else if (tipo=="semana") {
        var dias = rg(7);
        xaxis.label="Días de la semana";
        xaxis.divisor = 52;
        xaxis.vals = {
          "keys": dias.map(function(x){return "W"+x}),
          "legend": dias.map(function(x) {
            return ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][x]
          })
        }
      } else if (tipo=="year") {
        var meses = rg(1, 13);
        xaxis.label="Meses del año";
        xaxis.divisor = 1;
        xaxis.vals = {
          "keys": meses.map(function(x){return "M"+x}),
          "legend": meses.map(function(x) {
            return ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x-1]
          })
        }
      }
      var year=parseInt($("#yearsTiempoNormal").val(), 10);//.map(function(x){return Number(x)});
      if (isNaN(year)) year=null;
      var data={};
      Object.entries(obj).forEach(([y, value]) => {
        y = parseInt(y, 10);
        if (year==null || y==year) {
          Object.entries(value).forEach(([k, v]) => {
            if (xaxis.vals.keys.indexOf(k)!=-1) {
              k=k.substr(1)
              if (data[k]==null) data[k]=v;
              else {
                data[k]=zip_dict(data[k],v, function(a,b){return a+b})
              }
            }
          });
        }
      });
      Object.values(data).forEach((item, i) => {
        item["todo"]=Object.values(item).reduce(function(a,b){return a+b}, 0);
      });
      data = parseObj(data);
      xaxis.divisor = xaxis.divisor*(year?1:($("#yearsTiempoNormal option").length-1));
      var mk_promedio=function(x) {
        var a=x/xaxis.divisor;
        var b=Math.round(a);
        return b==0 && a!=0?(Math.round(a*10)/10):b;
      }
      var dataset = [];
      var ks = Object.keys(data["values"][0]);
      array_move(ks, "todo", 0);
      for (i=0; i<ks.length; i++) {
        k = ks[i];
        var color = dcd(k,
          "todo", "black",
          "noticias", "green",
          "comentarios", "blue",
          "posts", "red",
          "lightcoral"
        );
        var val = gF(data, k, (options.porcentaje?2:null));
        if (!options.porcentaje) {
          val = val.map(mk_promedio);
        }
        dataset.push({
          label: (options.porcentaje?"% ":"")+k,
          data: val,
          fill: false,
          //backgroundColor: d_color.blue.backgroundColor,
          borderColor: color,
          borderWidth: 1,
          hidden: k!="todo",
        })
      }
      setGraphChart({
          id: this.find("canvas")[0],
          title: null,
          labels: xaxis.vals.legend,
          type: 'LineWithLine',
          destroy:true,
          //max_y: t=="prc_"?100:null,
          x_label: xaxis.label,
          porcentaje:options.porcentaje
      }, dataset);
  },
  "count_estados":function(obj, options) {
    var dataset = [];
    var i, k, kl;
    var ks = Object.keys(obj["values"][0]);
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      var color = dcd(k,
        "total", "black",
        "published", "green",
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
        hidden: k=="autodiscard",
        fill: k=="autodiscard",
        backgroundColor:k=="autodiscard"?color:null
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"],
        type: 'LineWithLine',
        max_y: options.porcentaje?100:null,
        destroy:true,
        porcentaje:options.porcentaje
    }, dataset);
  },
  "count_categorias_todas": function(obj, options) {
    var dataset = [];
    var i, k, kl, color;
    var ks = Object.keys(obj["values"][0]);
    var colors = ["black", "grey", "blue", "green", "SaddleBrown", "lightcoral", "yellow", "orange", "pink"];
    if (options.porcentaje) colors = colors.slice(1);
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      color = colors[i] || "grey";
      dataset.push({
        label: k,
        data: gF(obj, k),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: color,
        borderWidth: 1,
        hidden: k=="mnm" || k=="otros",
        fill: k=="otros",
        backgroundColor:k=="otros"?color:null
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"],
        type: 'LineWithLine',
        //max_y: t=="prc_"?100:null,
        destroy:true,
        porcentaje:options.porcentaje
    }, dataset);
  },
  "karma_general": function (obj, options) {
    var labels = obj["keys"];
    var negatives = gF(obj, "negatives");
    var positives = gF(obj, "positives");
    negatives = zip_arr(negatives, positives, function(a, b) {
      var n = a + b;
      n = a*100/n;
      return Math.round(n*100)/100;
    })
    /*
    var neg_com = gF(obj, "comment_negatives");
    neg_com = zip_arr(neg_com, gF(obj, "comment_total"), function(a, n) {
      if (n==0 || a==0) return 0;
      n = a*100/n;
      return Math.round(n*100)/100;
    })*/
    var dataset = [{
        label: "% votos negativos",
        data: negatives,
        backgroundColor: d_color.red.backgroundColor,
        borderColor: d_color.red.borderColor,
        borderWidth: 1
      },{
        label: "Karma noticias (media)",
        data: gF(obj, "karma"),
        fill: false,
        borderColor: "orange",
        borderWidth: 1,
        hidden: true
      },{
        label: "Karma comentarios (media)",
        data: gF(obj, "comment_karma"),
        fill: false,
        borderColor: "Lime",
        borderWidth: 1,
        hidden: true
      }/*,{
        label: "% comentarios negativizados",
        data: neg_com,
        fill: false,
        borderColor: "lightcoral",
        borderWidth: 1
      }{
        label: "% votos positivos",
        data: gF(obj, "positives"),
        backgroundColor: d_color.blue.backgroundColor,
        borderColor: d_color.blue.borderColor,
        borderWidth: 1
      },{
        label: "Comentarios (media)",
        data: gF(obj, "comments"),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: "green",
        borderWidth: 1,
        hidden: true
      },{
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
        type: 'LineWithLine',
        destroy:true,
        porcentaje:options.porcentaje
    }, dataset);
  },
  "dominios_todos": function(obj, options) {
    var dataset = [];
    var i, t, k, kl, color;
    var ks={};
    if (!options.porcentaje) ks["total"]=["total"];

    obj["values"].forEach(function(v) {
      Object.keys(v).forEach(function(k) {
        if (ks[k]!=null) return;
        options.tags.forEach(function(t) {
          if (k==t) {
            ks[t]=[t];
          }/* else if (t.startsWith("*.") && (k.endsWith(t.substr(1)) || k==t.substr(2))) {
            var a = ks[t] || [];
            if (ks[t]==null) ks[t]=[k];
            else if (ks[t].indexOf(k)==-1) ks[t].push(k)
          }*/
        });
      });
    })
    /*
    if (options.tags.indexOf("AEDE")>-1) {
      ks["AEDE"]=[];
      obj["values"].forEach(function(v) {
        Object.keys(v).forEach(function(k) {
          DOM_AEDE.forEach(function(a) {
            if (ks["AEDE"].indexOf(k)>-1) return;
            if (k==a || k.endsWith("."+a)) {
              ks["AEDE"].push(k);
            }
          });
        })
      });
    }
    */
    var colors = (options.porcentaje)?DFL_COLOR.slice(1):DFL_COLOR;
    for (const [k, doms] of Object.entries(ks).sort(function(a,b){
      var i1=options.tags.indexOf(a[0]);
      var i2=options.tags.indexOf(b[0]);
      return i1-i2;
    })) {
      color = colors[dataset.length] || "grey";
      var values=gF(obj, doms[0]);
      for (i=1;i<doms.length;i++) values = zip_arr(values, gF(obj, doms[i]), function(a,b){return a+b})
      if (options.porcentaje) values = values.map(function(x){return Math.round(x*100)/100})
      dataset.push({
        label: k,
        data: values,
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: color,
        borderWidth: 1,
        hidden: k == "total"
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"],
        type: 'LineWithLine',
        //max_y: t=="prc_"?100:null,
        destroy:true,
        porcentaje:options.porcentaje
    }, dataset);
  },
  "tags_portada": function(obj, options) {
    var dataset = [];
    var i, t, k, kl, color;
    var ks={};
    if (!options.porcentaje) ks["total"]=["total"];
    obj["values"].forEach(function(v) {
      Object.keys(v).forEach(function(k) {
        if (ks[k]!=null) return;
        options.tags.forEach(function(t) {
          if (k==t) {
            ks[t]=[t];
          }
        });
      });
    })
    var colors = (options.porcentaje)?DFL_COLOR.slice(1):DFL_COLOR;
    for (const [k, doms] of Object.entries(ks).sort(function(a,b){
      var i1=options.tags.indexOf(a[0]);
      var i2=options.tags.indexOf(b[0]);
      return i1-i2;
    })) {
      color = colors[dataset.length] || "grey";
      var values=gF(obj, doms[0]);
      for (i=1;i<doms.length;i++) values = zip_arr(values, gF(obj, doms[i]), function(a,b){return a+b})
      if (options.porcentaje) values = values.map(function(x){return Math.round(x*100)/100})
      dataset.push({
        label: k,
        data: values,
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: color,
        borderWidth: 1,
        hidden: k == "total"
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"],
        type: 'LineWithLine',
        //max_y: t=="prc_"?100:null,
        destroy:true,
        porcentaje:options.porcentaje
    }, dataset);
  },
  "actividad": function(obj, options) {
      var dataset = [];
      var i, k, kl, color, values;
      //var ks = ["usuarios activos", "noticias", "comentarios", "usuarios creados", "usuarios eliminados"];
      var ks = Object.keys(obj["values"][0]).sort();
      var colors = DFL_COLOR;//["blue", "green", "SaddleBrown"];
      if (options.porcentaje) colors = colors.slice(1);
      var user_values;
      if (options.agrupar) {
        user_values=[];
        obj["keys"].forEach(function(k){
          user_values.push(modelos_aux["actividad"][k]);
        });
      } else {
        user_values=gF(obj, "usuarios activos");
      }
      var promedio = options.jq.find("*[name=promedio]").val()=="1";
      for (i=0; i<ks.length; i++) {
        k = ks[i];
        if (promedio && ["comentarios", "noticias", "posts"].indexOf(k)==-1) continue;
        if (k=="usuarios activos") {
          values = user_values;
        } else {
          values=gF(obj, k);
        }
        if (promedio) {
          values = zip_arr(values, user_values, function(a,b){return Math.round(a/b);})
          k = k +" / usuario";
        }
        color = colors[i] || "grey";
        dataset.push({
          label: k,
          data: values,
          fill: false,
          //backgroundColor: d_color.blue.backgroundColor,
          borderColor: color,
          borderWidth: 1
        })
      }
      setGraphChart({
          id: this.find("canvas")[0],
          title: null,
          labels: obj["keys"],
          type: 'LineWithLine',
          //max_y: t=="prc_"?100:null,
          destroy:true,
          porcentaje:options.porcentaje
      }, dataset);
    }
}
render_builder["count_categorias_published"] = render_builder["count_categorias_todas"];
render_builder["karma_portada"] = render_builder["karma_general"];
render_builder["dominios_portada"] = render_builder["dominios_todos"];
