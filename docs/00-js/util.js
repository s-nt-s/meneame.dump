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
