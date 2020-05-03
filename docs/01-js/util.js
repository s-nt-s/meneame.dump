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

function zip_arr() {
  var fnc = arguments[arguments.length-1];
  var isFnc = (typeof fnc === "function");
  var i;
  var arr=[];
  var params = Array.from(arguments);
  if (isFnc) params = params.slice(0, params.length-1);
  var sz = params.reduce(function(a,b){
    return Math.max(a,b.length)
  }, 0);
  rg(sz).forEach(function(c){
    var item=[];
    for (i=0;i<params.length;i++) item.push(params[i][c]);
    if (isFnc) item = fnc.apply(this, item);
    arr.push(item)
  });
  return arr;
}
