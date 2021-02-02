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
