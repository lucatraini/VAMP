function double_histByLatency(path,service,occ,checked,start,end){
    document.getElementById("reset").onclick=function(){myfunction()};
    console.log(occ)
  function myfunction() {
    //console.log(data)
    d3.select(".barchart")
    .select("svg").select("g").selectAll(".bar2")
    .remove()

    d3.select(".my_dataviz")
    .select("svg").select("g").selectAll(".bar")
    .attr("fill","lightblue")
  }
    d3.select(".barchart")
    .select("svg").select("g").selectAll(".bar2")
    .remove()
    //d3.select(".barchart")
        //.select("svg").remove()
    //d3.json("get_bins2?string="+encodeURIComponent(path)+"&number="+occ, function(error, bins2) {
      d3.json("get_bins/"+service+"/"+start+"/"+end, function(error, bins1) {
        if (error) throw error;
        d3.json("get_binsByLatency?string="+encodeURIComponent(path)+"&string2="+occ+"&number1="+start+"&number2="+end, function(error, bins2) {
        if (error) throw error;
        console.log(bins1)
        console.log(bins2)

        d3.select(".barchart")
        .select("svg").remove()
        
        var selectedObject = [];
      var margin = {
            top: 20,
            right: 20,
            bottom: 30,
            left: 40
          };
    var width = 800 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;
  
        // 2. Set up your SVG
  const barGroup = d3.select(".barchart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", 
              "translate(" + margin.left + "," + margin.top + ")"); 
  
  // 3. Set up your scales
  const xScale1 = d3.scaleBand()
    .range([0, width])
    .domain(bins1.map(d => d.key));
  
  const yScale1 = d3.scaleLinear()
    .range([height, 0])
    .domain([0, d3.max(bins1, d => d.value)]);

    var brush = d3.brushX()

  // 3. Set up your scales
  const xScale2 = d3.scaleBand()
    .range([0, width])
    .domain(bins2.map(d => d.key));
  
  const yScale2 = d3.scaleLinear()
    .range([height, 0])
    .domain([0, d3.max(bins2, d => d.value)]);
  
  // Scale the range of the data in the domains
  xScale1.domain(bins1.map(function(d) { return d.key; }));
  yScale1.domain([0, d3.max(bins1, function(d) { return d.value; })]);
  
  // 4. Set up your axes
  const xAxis = d3.axisBottom(xScale1)
                .tickValues(xScale1.domain().filter(function(d,i){
                  console.log(parseInt(d))
                  return !(i%13)}));
                
  const yAxis = d3.axisLeft(yScale1);
  

  
  barGroup.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis)

  barGroup.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yScale1));
  

    barGroup.append("defs")
    .append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .style("fill","black")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", height);
    
    brush.extent([[0, 0], [width, height]])
    .on("brush", brushed)
    .on("end",brushend)
    .on('end', function(d){
      d3.select(".barchart")
        .select("svg").select("g").selectAll(".bar2")
        .remove()
      var selection = d3.event.selection;
      var x0= xScale1.domain()[Math.floor(selection[0]/xScale1.step())]
      var x1= xScale1.domain()[Math.floor(selection[1]/xScale1.step())]
      var range ={0: x0,
                  1: x1}
      if (checked === "Compare Occurrences") {
        console.log(x0,x1)
        console.log(checked)
          d3.json("getTrace/"+service_name+"/"+x0+"/"+x1+"/"+start+"/"+end, function(error, trace) {
          
          var obj = { Title: data, ID: trace,  Value: trace};
          console.log(trace)
          console.log(data)
          console.log(trace)
          
          selectedObject.push(obj);
          
          treeFromHist(trace, service_name,x0,x1,checked,start,end)
          
          for(i=0;i<trace.length;i++){
            console.log(trace[i].traceID)
          selection += "<tr style= color:" + ">    <td>" + trace[i].name+ "</td>    <td>" + trace[i].traceID+"</td>    <td>"+trace[i].duration;
          }
          document.getElementById("table").innerHTML = "<tr><td colspan = " + "4" + ">Data Selected: "+trace.length+" </td></tr>" + "<tr><th>Operation Name</th><th>TraceID</th><th>Duration</th></tr>" + selection;
      })
  } else{
    console.log("latency")
    console.log(x0,x1)
    checked="Compare Latency"
    console.log(checked)
    
    d3.json("compareGroupsLatency/"+service_name+"/"+x0+"/"+x1+"/"+start+"/"+end, function(error, trace) {
      
      var obj = {  ID: trace,  Value: trace};
      console.log(trace)
      
      selectedObject.push(obj);
      
      treeFromHist(trace, service_name,x0,x1,checked,start,end)
      
    })
  }
  });



  barGroup.selectAll(".bar1")
    .data(bins1)
    .enter()
    .append("rect")
    .attr("class", "bar1")
    .attr("x", function(d) { return xScale1(d.key); })
    .attr("y", function(d) { return yScale1(d.value); })
    .attr("width", xScale1.bandwidth())
    .attr("height", function(d) { return height - yScale1(d.value); })
    .attr("fill", "steelblue");

  barGroup.selectAll(".bar2")
    .data(bins2)
    .enter()
    .append("rect")
    .attr("class", "bar2")
    .attr("x", function(d) { return xScale1(d.key); })
    .attr("y", function(d) { return yScale1(d.value); })
    .attr("width", xScale1.bandwidth())
    .attr("height", function(d) { return height - yScale1(d.value); })
    .attr("fill","rgba(255, 0, 0, 0.4)");
    
    barGroup.append("g")
    .attr("class", "x brush")
    .call(brush) //call the brush function, causing it to create the rectangles
    .selectAll("rect") //select all the just-created rectangles
    .attr("y", -6)
    .attr("height", (height + margin.top)) //set their height

    barGroup.select(".selection")
    .style("fill", "red")
    .style("fill-opacity", 0.3);
    
    
    barGroup.selectAll(".handle")
        .style("fill","black");


    barGroup.selectAll(".bar1")
    .on("mouseover", function() {
    d3.select(this)
    .attr("fill", "red");
    })
    .on("mouseout", function() {
    d3.select(this)
    .attr("fill", "steelblue");
    });
    
    barGroup.selectAll(".bar2")
    .on("mouseover", function() {
    d3.select(this)
    .attr("fill", "red");
    })
    .on("mouseout", function() {
    d3.select(this)
    .attr("fill","rgba(255, 0, 0, 0.4)");
    });
    
     
  
    function brushend() {
      if (brush.empty()){
      barGroup.select("#clip>rect")
      .attr("x", 0)
      .attr("width", width)
      .style("fill","red");
      }
      }
      
      function brushed() {
      var e = d3.event.selection;
      barGroup.select("#clip>rect")
      .attr("x", e[0])
      .attr("width", e[1] - e[0])
      .style("fill","red");
      }
      
      function clearBrush(){
      var selection = "";
      var selectedObject = [];
      j=[];
      brush
      .clear()
      .event(d3.select(".brush"));
      document.getElementById("table").innerHTML = "<tr><td colspan = " + "4" + ">Data Selected:  </td></tr>" + "<tr><th>ID</th><th>Name</th></tr>"+selection;
      }
    })

  }) 
}