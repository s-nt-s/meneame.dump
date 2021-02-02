render_builder={
  "abandono": function(obj, options) {
    var nostay = this.find("#nostay").is(":checked");
    var labels=[];
    var data=[];
    var color=[];
    obj.forEach((item, i) => {
      var l=item[0];
      if (l==9999) {
        if (nostay) return;
        l="∞";
        color.push(d_color.green)
      } else if (i==0) {
        color.push(d_color.red)
      } else {
        color.push(d_color.blue)
      }
      if (l==9998) l=">12";
      labels.push(l);
      data.push(item[1]);
    });
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: labels,
        type: "bar",
        x_label: "meses entre el strike y el abandono",
        y_label: "número de usuarios",
        destroy:true,
        tooltips: {
          title: function(i, data) {
            return "";
          },
          label: function(i, data) {
            var t = strikes["users"].length;
            var u = i.value;
            var p = round((Number(u) / t) * 100);
            var m = i.label;
            var w = Math.max(u.length, m.length);
            w = w - u.length;
            var s="";
            while (s.length<w) s=s+"\u2007";
            if (m=="∞") {
              if (u==1) return `${s}${u} usuario (${p}%) aún no han abandonado`;
              return `${s}${u} usuarios (${p}%) aún no han abandonado`;
            }
            if (m==0) {
              if (u==1) return `${s}${u} usuario (${p}%) abandono`;
              return `${s}${u} usuarios (${p}%) abandonaron`;
            }
            if (m.startsWith(">")) {
              if (u==1) return `${s}${u} usuario (${p}%) abandono despues de`;
              return `${s}${u} usuarios (${p}%) abandonaron despues de`;
            }
            if (u==1) return `${s}${u} usuario (${p}%) abandono a`;
            return `${s}${u} usuarios (${p}%) abandonaron a`;
          },
          afterLabel: function(i, data) {
            var u = i.value;
            var m = i.label;
            if (m=="∞") return "";
            var w = Math.max(u.length, m.length);
            w = w - m.length;
            var s="";
            while (s.length<w) s=s+"\u2007";
            if (m==0) return "el mismo día de su último strike";
            if (m==1) return `${s}${m} mes de su último strike`;
            if (m.startsWith(">")) {
              m = m.substr(1);
              w = w + 1;
              var s="";
              while (s.length<w) s=s+"\u2007";
              return `${s}${m} meses o MÁS de su último strike`;
            }
            return `${s}${m} meses de su último strike`;
          }
        }
    }, [{
        data: data,
        borderWidth: 1,
        backgroundColor: color.map(function(c){return c.backgroundColor}),
        borderColor: color.map(function(c){return c.borderColor})
    }])
  },
  "timeline": function(obj, options) {
    var dataset = [];
    var i, k, kl, color, hidden;
    var ks = Object.keys(obj["values"][0]);
    var divby=null;
    var divlb=null;
    if (options.transformacion && ks.indexOf(options.transformacion)>=0) {
      divby=gF(obj, options.transformacion);
      divlb=options.transformacion.substr(0, options.transformacion.length-1);
    }
    for (i=0; i<ks.length; i++) {
      k = ks[i];
      if (k=="usuarios" || k=="comentarios") continue;
      hidden = strikes["total"][k]<6;
      color = DFL_COLOR[options.porcentaje?(i+1):i] || "grey";
      var data = gF(obj, k);
      if (divby!=null) {
        data = zip_arr(data, divby, function (a, b){
          return round(a/b, 0, 2);
        })
        k = k + " / " + divlb;
      }
      dataset.push({
        label: k,
        data: data,
        fill: false,
        borderColor: color,
        //backgroundColor: d_color.blue.backgroundColor,
        borderWidth: 1,
        hidden: hidden
      })
    }
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj["keys"],
        type: 'LineWithLine',
        max_y: options.porcentaje?100:null,
        destroy:true,
        porcentaje:options.porcentaje,
        eqlabel:function(a, b) {
          a = a.split(/\//)[0].trim();
          b = b.split(/\//)[0].trim();
          return b==a;
        }
    }, dataset);
  },
  "poblacion": function(obj, options) {
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: obj.keys,
        type: "bar",
        x_label: "En menéame desde...",
        y_label: "% de usuarios",
        destroy:true,
        tooltips: {
          title: function(i, data) {
            return "";
          },
          label: function(i, data) {
            var total=null;
            var tp=null;
            if (i.datasetIndex==0) {
              tp = "strikes"
              total = modelos["poblacion"].values[i.index]["strikes"];
            } else {
              tp = "comentarios"
              total = modelos["poblacion"].values[i.index]["poblacion"];
            }
            var p = round(i.value);
            if (p==0) return `0 usuarios con ${tp}`;
            return `el ${p}% de los usuarios (${total}) con ${tp}`;
          },
          afterLabel: function(i, data) {
            var u = i.value;
            if (round(i.value)==0) return "";
            var m = i.label;
            return `estan en menéame desde ${m}`;
          }
        }
    }, [{
        label: "Usuarios con strike",
        data: gF(obj, "strikes", true),
        borderWidth: 1,
        backgroundColor: d_color.red.backgroundColor,
        borderColor: d_color.red.borderColor
    },{
        label: "Usuarios con comentarios",
        data: gF(obj, "poblacion", true),
        borderWidth: 1,
        backgroundColor: d_color.blue.backgroundColor,
        borderColor: d_color.blue.borderColor
    }])
  },
  "_poblacion": function(obj, options) {
    var ctx = this.find("canvas")[0].getContext('2d');
    var i;
    var color = rg(Object.keys(obj).length).map(function(i){
      return DFL_COLOR[i%DFL_COLOR.length];
    })
    var myPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            datasets: [{
                data: Object.values(obj),
                backgroundColor: color
            }],
            labels: Object.keys(obj)
        },
        options: {
        tooltips: {
            callbacks: {
              label: function(i, data) {
                var dt=data.datasets[i.datasetIndex];
                var tt=dt.data.reduce((a, b) => a + b, 0);
                var p = (dt.data[i.index]/tt)*100;
                p = round(p)
                return p+" % son del año "+data.labels[i.index];
              }
            }
          }
        }
    });
    myPieChart.update()
    /*
    setGraphChart({
        id: this.find("canvas")[0],
        title: null,
        labels: Object.keys(obj),
        type: 'pie',
        porcentaje:true
    }, [{
      data:Object.values(obj)
    }]);
    */
  }
}
