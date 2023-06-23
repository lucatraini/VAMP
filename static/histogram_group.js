/*
   async function fetchTrace(){
    try{
      const response = await fetch("http://127.0.0.1:5000/getRange");
      if(!response.ok){
        throw new Error(`HTTP error: ${response.status}`);
      }
      const bins = await response.json();
      console.log(bins)
      return bins
    }
    catch(error){
      console.error(`Could not get products: ${error}`)
    }
   }
*/
function drawHist(start,end,checked){
  console.log("START")
  console.log(start,end)
  d3.select(".barchart").select("svg").remove()
    console.log(service_name)
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

  var brush = d3.brushX()
  
         
  
  
  var chart = d3.select(".barchart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", 
              "translate(" + margin.left + "," + margin.top + ")"); 
  



d3.json("/get_bins/"+service_name+"/"+start+"/"+end, function(error, data) {
    if (error) throw error;
    console.log(data)

    // Scale the range of the data in the domains
    xc.domain(data.map(function(d) { return d.key; }));
    yc.domain([0, d3.max(data, function(d) { return d.value; })]);

    // format the data
    data.forEach(function(d) {
    d.value = +d.value;
    });

    chart.append("defs")
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
        var selection = d3.event.selection;
        var x0= xc.domain()[Math.floor(selection[0]/xc.step())]
        var x1= xc.domain()[Math.floor(selection[1]/xc.step())]
        var range ={0: x0,
                    1: x1}
        if (checked === "Compare Occurrences") {
          console.log(x0,x1)
          console.log(checked)
            d3.json("getTrace/"+service_name+"/"+x0+"/"+x1+"/"+start+"/"+end, function(error, trace) {
            console.log(trace)
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
        
        var obj = { Title: data, ID: trace,  Value: trace};
        console.log(trace)
        console.log(data)
        console.log(trace)
        
        selectedObject.push(obj);
        
        treeFromHist(trace, service_name,x0,x1,checked,start,end)
        
      })
    }
    });
    
    
    chart.selectAll(".barchart")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return xc(d.key); })
    .attr("width", xc.bandwidth())
    .attr("y", function(d) { return yc(d.value); })
    .attr("height", function(d) { return height - yc(d.value); })
    .attr("fill","steelblue");

    chart.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function(d) { return xc(d.key); })
    .attr("width", xc.bandwidth())
    .attr("y", function(d) { return yc(d.value); })
    .attr("height", function(d) { return height - yc(d.value); })
    .attr("fill","steelblue");

    var xAxis = d3.axisBottom(xc)
                    .tickValues(xc.domain().filter(function(d,i){
                      console.log(parseInt(d))
                      return !(i%13)}))
    
    chart.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    
    chart.append("text") //Add chart title
    .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom+50) + ")")
    .style("text-anchor", "middle")
    .text("Chart");
    
    chart.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yc));

    chart.append("g")
    .attr("class", "x brush")
    .call(brush) //call the brush function, causing it to create the rectangles
    .selectAll("rect") //select all the just-created rectangles
    .attr("y", -6)
    .attr("height", (height + margin.top)) //set their height
    
    chart.select(".selection")
    .style("fill", "red")
    .style("fill-opacity", 0.3);
    
    
    chart.selectAll(".handle")
        .style("fill","black");
    

    function resizePath(d) {
    var e = +(d == "e"),
        xc = e ? 1 : -1,
        yc = height / 3;
    return "M" + (.5 * xc) + "," + yc + "A6,6 0 0 " + e + " " + (6.5 * xc) + "," + (yc + 6) + "V" + (2 * yc - 6) + "A6,6 0 0 " + e + " " + (.5 * xc) + "," + (2 * yc) + "Z" + "M" + (2.5 * xc) + "," + (yc + 8) + "V" + (2 * yc - 8) + "M" + (4.5 * xc) + "," + (yc + 8) + "V" + (2 * yc - 8);
    }

    chart.selectAll(".resize").append("path").attr("d", resizePath);
});





function brushend() {
if (brush.empty()){
chart.select("#clip>rect")
.attr("x", 0)
.attr("width", width)
.style("fill","red");
}
}

function brushed() {
var e = d3.event.selection;
chart.select("#clip>rect")
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
}

/*
async function fetchRange(){
try{
const response = await fetch("http://127.0.0.1:5000/getRange");
if(!response.ok){
throw new Error(`HTTP error: ${response.status}`);
}
const bins = await response.json();
console.log(bins)
return bins
}
catch(error){
console.error(`Could not get products: ${error}`)
}
}
function get_trace(){
// get the data
d3.json("getRange", function(error, data) {
if (error) throw error;
// format the data
data.forEach(function(d) {
d.value = +d.value;
});
console.log(data)
var obj = { Title: data, ID: j,  Value: j};
    selectedObject.push(obj);
    for(i=0;i<j.length;i++){
    selection += "<tr style= color:" + ">    <td>" + j[i].key + "</td>    <td>" + j[i].value;
    }
    document.getElementById("table").innerHTML = "<tr><td colspan = " + "4" + ">Data Selected: "+j.length+" </td></tr>" + "<tr><th>ID</th><th>Value</th></tr>" + selection;

})
}
*/