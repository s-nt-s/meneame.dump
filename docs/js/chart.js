function setGraphChart(obj, dataset) {
    if (obj.id==null) obj.id = "myChart";
    if (obj.type==null) obj.type = "bar";
    var elem = document.getElementById(obj.id)
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
    var i;
    for (i=0; i<dataset.length && !dat.options.legend;i++) {
      if (dataset[i].label==null) dat.options.legend={display:false};
    }
    var myChart = new Chart(ctx, dat);
    if (dataset.length>1) {
      if (obj.max_y==null) obj.max_y = myChart.scales["y-axis-0"].max;
      myChart.options.scales.yAxes[0].ticks.max = obj.max_y;
    }
    $(elem).data("chart", myChart);
    return myChart;
}

function gF(obj, key){
  return obj["values"].map(function(x){return Math.round(x[key])})
}

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

function chartMensual(value) {
  var t = Number(value || $("#tipoMensual").val());
  obj = t==1?data_mensual:data_mensual_portada;
  var labels = obj["keys"].map(function(x) {return x.toFixed(2);})
  var dataset = [{
        label: "Karma",
        data: gF(obj, "karma"),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: "orange",
        borderWidth: 1
    },{
        label: "Votos positivos",
        data: gF(obj, "votes"),
        backgroundColor: d_color.blue.backgroundColor,
        borderColor: d_color.blue.borderColor,
        borderWidth: 1
    },{
        label: "Votos negativos",
        data: gF(obj, "negatives"),
        backgroundColor: d_color.red.backgroundColor,
        borderColor: d_color.red.borderColor,
        borderWidth: 1
    },{
        label: "Comentarios",
        data: gF(obj, "comments"),
        fill: false,
        //backgroundColor: d_color.blue.backgroundColor,
        borderColor: "green",
        borderWidth: 1
    }
  ];
  var ch = $("#data_mensual").data("chart");
  if (ch) ch.destroy();
  setGraphChart({
      id: 'data_mensual',
      title: "Media mensual",
      labels: labels,
      type: 'line'
  }, dataset);
}

$(document).ready(function(){
  chartMensual();
  $("#tipoMensual").change(function(){chartMensual(this.value)})
})
