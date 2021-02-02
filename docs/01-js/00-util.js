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

function zip_dict() {
  var fnc = arguments[arguments.length-1];
  var isFnc = (typeof fnc === "function");
  var i;
  var dict={};
  var params = Array.from(arguments);
  if (isFnc) params = params.slice(0, params.length-1);
  params.forEach(function(p){
    Object.entries(p).forEach(([key, value]) => {
        if (dict[key]==null) dict[key]=[];
        dict[key].push(value);
    });
  });
  if (isFnc) {
    Object.keys(dict).forEach(function(key) {
        dict[key]=fnc.apply(this, dict[key]);
    });
  }
  return dict;
}
function array_move(arr, element, new_index) {
  var old_index = arr.indexOf(element);
  if (new_index>=arr.length) new_index = arr.length -1;
  if (old_index==-1 || old_index==new_index) return arr;
  arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
  return arr;
};

function round(p, dec, sig) {
  if (typeof p == "string") p = Number(p);
  if (isNaN(p) || Math.trunc(p)==p) return p;
  if (dec==null) dec=0;
  if (sig==null) sig=1;
  if (sig==0 && dec==0) return Math.round(p);
  while (true) {
    var m = Math.pow(10, dec);
    var x = Math.round(p*m)/m;
    if (x!=0) {
      if (sig==1) return x;
      var s = x.toString().replace(/^[0\.]+/, "");
      if (s.length>=sig) return x;
    }
    dec = dec + 1;
  }
}

function toNum(x, dft) {
  if (x==null) return null;
  var n=parseFloat(x, 10);
  if (arguments.length==1 || !isNaN(n)) return n;
  return dft;
}
