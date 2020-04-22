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
  if (t.find("*[name=agrupar]").val()=="trimestre") {
    var _mdl = {
      "keys": [],
      "values": []
    }
    var re_index={}
    var last_tri=null;
    mdl["keys"].forEach(function(item, i) {
      var lst = _mdl["keys"].length-1;
      var y=Math.floor(item);
      var m=(item*100)-(y*100);
      if (lst==-1 && !(m==1 || m==4 || m==7 || m==10)) return;
      var t=y + (dcd(m,
        1,1,2,1,3,1,
        4,2,5,2,6,2,
        7,3,8,3,9,3,
        4
      )/100);
      if (lst>=0 && _mdl["keys"][lst]==t) {
        re_index[i]=lst;
      } else {
        _mdl["keys"].push(t);
        re_index[i]=lst+1;
      }
      if (m==3 || m==6 || m==9 || m==12) last_tri=_mdl["keys"].length;
    })
    _mdl["keys"]=_mdl["keys"].slice(0, last_tri);
    mdl["values"].forEach(function(v, i){
      var new_index = re_index[i];
      if (new_index==null || new_index>=_mdl["keys"].length) return;
      var new_value = _mdl["values"][new_index];
      if (new_value==null) {
        _mdl["values"].push(v);
      } else {
        Object.entries(v).forEach(([key, value]) => {
            new_value[key]=new_value[key]+value;
        });
        _mdl["values"][new_index]=new_value;
      }
    });
    mdl=_mdl;
  }
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
      var prov = zip_arr(prc?gF(data, "todas"):td, prc?gF(data, "published"):pb, function (tot, pub) {
        return Math.round((pub/tot)*10000)/100;
      })
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
        },{
          label: "% probabilidad de llegar a portada",
          data: prov,
          fill: false,
          //backgroundColor: d_color.blue.backgroundColor,
          borderColor: "orange",
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
        hidden: k=="autodiscard",
        fill: k=="autodiscard",
        backgroundColor:k=="autodiscard"?color:null
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
    var i, k, kl, color;
    var ks = Object.keys(obj["values"][0]);
    var colors = ["black", "grey", "blue", "green", "SaddleBrown", "lightcoral", "yellow", "orange", "pink"];
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      color = colors.slice(prc?1:0)[i] || "grey";
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
        labels: obj["keys"].map(function(x) {return x.toFixed(2);}),
        type: 'line',
        //max_y: t=="prc_"?100:null,
        destroy:true
    }, dataset);
  },
  "karma_general": function (obj, prc) {
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
        type: 'line',
        destroy:true
    }, dataset);
  }
}
render_builder["count_categorias_published"] = render_builder["count_categorias_todas"];
render_builder["karma_portada"] = render_builder["karma_general"];
