var t_strikes=strikes["reasons"].map(function(r){
  return {
    "label": r,
    "value": 0
  }
})
strikes["strikes"].forEach((s, i) => {
    t_strikes[s["reason"]].value = t_strikes[s["reason"]].value+1;
});
t_strikes.sort(function(b,a){
  var x = a.value-b.value;
  if (x!=0) return x;
  return a.label.localeCompare(b.label)
});
strikes["total"]={};
t_strikes.forEach((s, i) => {
    strikes["total"][s.label]=s.value;
});


var modelos = {
  "abandono": function() {
    var pre=this.find("select[name=presencia]").val();
    var tdt=this.find("select[name=abandono]").val();
    pre = (pre!=null && pre.length)?Number(pre):null;
    var index = strikes["users"].map(function(u){
      if (pre==null || u["abandono"]==null) return u;
      var ini = u["create"];
      var fin = u[tdt];
      if (fin==null) return u;
      var dy=Math.round((fin-ini)/(1000*60*60*24));
      if (dy<=pre) return null;
      return u;
    })
    var data={};
    strikes["strikes"].forEach((s, i) => {
      var id=s['user'];
      var user = index[s['user']]
      if (user==null) return;
      var ud = user[tdt];
      if (ud==null) {
        data[id]=null;
        return;
      }
      var us=s["date"];
      var dy=Math.round((ud-us)/(1000*60*60*24));
      if (data[id]==null || data[id]>dy) data[id]=dy;
    });
    var points={};
    for (const dy of Object.values(data)) {
      var x = dy==null?9999:Math.ceil(dy / 30);
      if (x>12 && x!=9999) {
        x=9998
      }
      //x=dy;
      points[x]=(points[x] || 0)+1;
    }
    points = Object.entries(points);
    points.sort(function(a, b) {
      return a[0]-b[0];
    });
    return points;
  },
  "creacion": (function(){
    var points={};
    strikes["strikes"].forEach((s, i) => {
      var id=s['user'];
      var ud=strikes["users"][s['user']]["create"];
      ud = ud.getFullYear();//+((ud.getMonth()+1)/100)
      points[ud]=(points[ud] || 0)+1;
    });
    points = Object.entries(points);
    points.sort(function(a, b) {
      return a[0]-b[0];
    });
    return points;
  })(),
  "poblacion": (function(){
    var data={};
    for (const [y, p] of Object.entries(strikes["poblacion"])) {
      data[y]={
        "poblacion":p,
        "strikes": 0
      }
    }
    strikes["strikes"].forEach((s, i) => {
      var id=s['user'];
      var ud=strikes["users"][s['user']]["create"];
      ud = ud.getFullYear();//+((ud.getMonth()+1)/100)
      if (data[ud]==null) {
        data[ud]={
          "poblacion":0,
          "strikes": 0
        }
      }
      data[ud].strikes=data[ud].strikes+1;
    });
    return data;
  })(),
  "timeline": (function(){
    var data={};
    var obj={"total":0};
    Object.keys(strikes["total"]).forEach((s, i) => {obj[s]=0;});
    strikes["strikes"].forEach((s, i) => {
      var dt=s["date"];
      dt = dt.getFullYear()+((dt.getMonth()+1)/100);
      var rs = strikes["reasons"][s['reason']];
      if (data[dt]==null) data[dt]={...obj};
      data[dt][rs] = data[dt][rs]+1;
      data[dt]["total"] = data[dt]["total"]+1;
    });
    return data;
  })(),
  "_poblacion": strikes["poblacion"]
}
function parseObj(obj) {
  var keys = Object.keys(obj).map(function(x){
    return Number(x);
  }).sort(function(a, b){return a-b});
  //keys = keys.slice(0, keys.length-6);
  var r = {"keys": keys, "values": []};
  var i, v;
  for (i=0;i<keys.length;i++) {
    v = obj[keys[i]];
    r["values"].push(v);
  }
  r.__parsed__ = true;
  return r;
}
modelos["timeline"]=parseObj(modelos["timeline"]);
modelos["poblacion"]=parseObj(modelos["poblacion"]);
