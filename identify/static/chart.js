function drawchart(input, div_name, title) {

        // Trending
        var prepopular = input;
        console.log(prepopular)

        prepopular = prepopular.replace(/&quot;/g,'"');
        console.log(prepopular)
        var popular = JSON.parse(prepopular);
        console.log(popular)

        google.charts.load('current', {'packages':['corechart']});
        google.charts.setOnLoadCallback(drawChart);

        function drawChart() {

          var data = new google.visualization.DataTable();

          data.addColumn("string", "Title");
          data.addColumn("number", "Count");

          var size = Object.keys(popular).length;
          data.addRows(size);

          var i;
          var max_value = popular[0]['count'];
          for (i = 0; i < size; i++) {
            data.setCell(i, 0, popular[i]['title']);
            // console.log(popular[i]['title'])
            data.setCell(i, 1, popular[i]['count']);
            if(popular[i]['count'] > max_value) {
              max_value = popular[i]['count'];
            }
            // console.log(popular[i]['count'])
          }
          var view = new google.visualization.DataView(data);
          console.log("max_value:"+ max_value);

          var options = {
            title: title,
            width: 500,
            height: 800,
            bar: {groupWidth: "70%"},
            legend: { position: "none" },
            hAxis: { 
                viewWindowMode:'explicit',
                viewWindow: {
                    max:max_value,
                    min:0
                }
            }
          };
          var chart = new google.visualization.BarChart(document.getElementById(div_name));
          chart.draw(view, options);
          
        }  
}   