function linking(data,value){
  document.getElementById("reset").onclick=function(){myfunction()};

  function myfunction() {
    console.log(data)
    
    d3.select(".barchart")
    .select("svg").select("g").selectAll(".bar2")
    .data(data).remove()

    d3.select(".my_dataviz").select("svg").remove()
  }
  console.log(data)
    d3.select(".barchart")
        .select("svg").select("g").selectAll(".bar_2")
        .data(data).remove()
    var margin = {
        top: 20,
        right: 20,
        bottom: 30,
        left: 40
      };    
      
      var selectedObject = [];
      var selection = "";
    
      var width = 800 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;
    
      var xc = d3.scaleBand()
        .range([0, width])
        .padding(0.1);
      
      var yc = d3.scaleLinear()
        .range([height, 0]);  
        // Scale the range of the data in the domains
        xc.domain(data.map(function(d) { return d.key; }));
        yc.domain([0, d3.max(data, function(d) { return d.value; })]);
    
        // format the data
        data.forEach(function(d) {
        d.value = +d.value;
        });
        
        
        d3.select(".barchart")
        .select("svg").select("g").selectAll(".barchart")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar_2")
        .attr("x", function(d) { return xc(d.key); })
        .attr("width", xc.bandwidth())
        .attr("y", function(d) { return yc(d.value); })
        .attr("height", function(d) { return height - yc(d.value); })
        .attr("fill","rgba(255, 0, 0, 0.5)");;
    
        d3.select(".barchart")
        .select("svg").select("g").selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar_2")
        .attr("x", function(d) { return xc(d.key); })
        .attr("width", xc.bandwidth())
        .attr("y", function(d) { return yc(d.value); })
        .attr("height", function(d) { return height - yc(d.value); })
        .attr("fill","rgba(255, 0, 0, 0.5)");
        

   /*
        chart.append("g")
        .attr("class", "x brush")
        .call(brush) //call the brush function, causing it to create the rectangles
        .selectAll("rect") //select all the just-created rectangles
        .attr("y", -6)
        .attr("height", (height + margin.top)) //set their height
       */
        d3.select(".barchart").selectAll("rect")
        .on("click", function(d) {
            console.log(d);
        });
        
    
        function resizePath(d) {
        var e = +(d == "e"),
            xc = e ? 1 : -1,
            yc = height / 3;
        return "M" + (.5 * xc) + "," + yc + "A6,6 0 0 " + e + " " + (6.5 * xc) + "," + (yc + 6) + "V" + (2 * yc - 6) + "A6,6 0 0 " + e + " " + (.5 * xc) + "," + (2 * yc) + "Z" + "M" + (2.5 * xc) + "," + (yc + 8) + "V" + (2 * yc - 8) + "M" + (4.5 * xc) + "," + (yc + 8) + "V" + (2 * yc - 8);
        }
    
        d3.select(".barchart").selectAll(".resize").append("path").attr("d", resizePath);
    
    
    
    
    
    /*
    function brushend() {
    if (brush.empty()){
    chart.select("#clip>rect")
    .attr("x", 0)
    .attr("width", width);
    }
    }
    
    function brushed() {
    var e = d3.event.selection;
    chart.select("#clip>rect")
    .attr("x", e[0])
    .attr("width", e[1] - e[0]);
    }
    
    function clearBrush(){
    var selection = "";
    var selectedObject = [];
    j=[];
    brush
    .clear()
    .event(d3.select(".brush"));
    document.getElementById("table").innerHTML = "<tr><td colspan = " + "4" + ">Data Selected:  </td></tr>" + "<tr><th>ID</th><th>Name</th></tr>"+selection;
    }*/
}