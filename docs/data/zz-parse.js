function parseObj(obj) {
  var keys = Object.keys(obj).map(function(x){return Number(x)}).sort();
  keys = keys.slice(0, keys.length-6);
  var r = {"keys": keys, "values": []};
  var i, v;
  for (i=0;i<keys.length;i++) {
    v = obj[keys[i]];
    r["values"].push(v);
  }
  /*
  var max_val = Math.max(...r["values"].map(function(x){
    return Math.max(...Object.values(x))
  }));
  var min_val = Math.min(...r["values"].map(function(x){
    return Math.min(...Object.values(x))
  }));
  r["max_val"]=Math.ceil(max_val);
  r["min_val"]=Math.floor(max_val);
  */
  return r;
}

data_mensual = parseObj(data_mensual);
data_mensual_portada = parseObj(data_mensual_portada);
