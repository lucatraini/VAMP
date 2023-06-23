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
  var margin = {
      top: 20,
      right: 20,
      bottom: 30,
      left: 40
    };    

    var selectedObject = [];
    var selection = "";

    var width = 800 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom;

    var x = d3.scaleBand()
      .range([0, width])
      .padding(0.1);
    
    var y = d3.scaleLinear()
      .range([height, 0]);  

    var brush = d3.brushX()
    
    
    var chart = d3.select(".barchart").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .call(d3.zoom().on("zoom", function () {
            svg.attr("transform", d3.event.transform)
         }))
          .append("g")
          .attr("transform", 
                "translate(" + margin.left + "," + margin.top + ")") ;
    

    var input = document.getElementById("service");
    input.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("myBtn").click();
      }
    });
    searchBox = document.querySelector("#searchBox");
    countries = document.querySelector("#service");
    var when = "change"; //You can change this to keydown, keypress or change
    
    searchBox.addEventListener("change", function (e) {
        var text = e.target.value; //searchBox value
        var options = countries.options; //select options
        for (var i = 0; i < options.length; i++) {
            var option = options[i]; //current option
            var optionText = option.text; //option text ("Somalia")
            var lowerOptionText = optionText.toLowerCase(); //option text lowercased for case insensitive testing
            var lowerText = text.toLowerCase(); //searchBox value lowercased for case insensitive testing
            var regex = new RegExp("^" + text, "i"); //regExp, explained in post
            var match = optionText.match(regex); //test if regExp is true
            var contains = lowerOptionText.indexOf(lowerText) != -1; //test if searchBox value is contained by the option text
            if (match || contains) { //if one or the other goes through
                option.selected = true; //select that option
                var value =option.value
                onChange(value)
                console.log(value)
                return ; //prevent other code inside this event from executing
            }
            console.log(value)
            searchBox.selectedIndex = 0; //if nothing matches it selects the default option
        }
    });
    // get the data
    var e = document.getElementById("service")
    console.log(e);
    function onChange(value) {
      d3.select(".my_dataviz")
        .select("svg").select(g).remove()
      d3.select("svg").remove()
      var value = e.value;
      console.log(value);

      var chart = d3.select(".barchart").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", 2000 + margin.top + margin.bottom)
          .call(d3.zoom().on("zoom", function () {
            svg.attr("transform", d3.event.transform)
         }))
          .append("g")
          .attr("transform", 
                "translate(" + margin.left + "," + margin.top + ")") ;
    
      d3.json("get_bins/"+ e.value, function(error, data) {
        if (error) throw error;
      
        // Scale the range of the data in the domains
        x.domain(data.map(function(d) { return d.key; }));
        y.domain([0, d3.max(data, function(d) { return d.value; })]);
    
        // format the data
        data.forEach(function(d) {
          d.value = +d.value;
        });
        
        chart.append("defs")
          .append("clipPath")
          .attr("id", "clip")
          .append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", width)
          .attr("height", height);
        
        
        brush.extent([[0, 0], [width, height]])
          .on("brush", brushed)
          .on("end",brushend)
          .on('end', function(d){
            var selection = d3.event.selection;
            var x0= x.domain()[Math.floor(selection[0]/x.step())]
            var x1= x.domain()[Math.floor(selection[1]/x.step())]
            var range ={0: x0,
                        1: x1}
              console.log(range)
            d3.json("getTrace/"+e.value+"/"+x0+"/"+x1, function(error, trace) {
    
            var obj = { Title: data, ID: trace,  Value: trace};
            selectedObject.push(obj);
            
            for(i=0;i<trace.length;i++){
              selection += "<tr style= color:" + ">    <td>" + trace[i].name+ "</td>    <td>" + trace[i].traceID+"</td>    <td>"+trace[i].duration;
            }
            document.getElementById("table").innerHTML = "<tr><td colspan = " + "4" + ">Data Selected: "+trace.length+" </td></tr>" + "<tr><th>Operation Name</th><th>TraceID</th><th>Duration</th></tr>" + selection;
          })
        });
          
          
        chart.selectAll(".barchart")
          .data(data)
          .enter().append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return x(d.key); })
          .attr("width", x.bandwidth())
          .attr("y", function(d) { return y(d.value); })
          .attr("height", function(d) { return height - y(d.value); });
    
        chart.selectAll(".bar")
          .data(data)
          .enter().append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return x(d.key); })
          .attr("width", x.bandwidth())
          .attr("y", function(d) { return y(d.value); })
          .attr("height", function(d) { return height - y(d.value); });
        
        var xAxis = d3.axisBottom(x)
                    .tickValues(x.domain().filter(function(d,i){ 
                      console.log(i)
                      return !(i%13)}))
        
        chart.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
          .selectAll("text")
          .attr("y", 0)
          .attr("x", 9)
          .attr("dx", "-2em")
          .attr("dy", ".35em")
          .attr("transform", "rotate(-60)")
          .style("text-anchor", "end");
        
        /*
        chart.append("text") //Add chart title
          .attr("transform", "translate(" + (width / 2) + " ," + (height+20) + ")")
          .style("text-anchor", "middle")
          .text("");
        */
        chart.append("g")
          .attr("class", "y axis")
          .call(d3.axisLeft(y));
    
        chart.append("g")
          .attr("class", "x brush")
          .call(brush) //call the brush function, causing it to create the rectangles
          .selectAll("rect") //select all the just-created rectangles
          .attr("y", -6)
          .attr("height", (height + margin.top)) //set their height
        
        
    
        function resizePath(d) {
          var e = +(d == "e"),
            x = e ? 1 : -1,
            y = height / 3;
          return "M" + (.5 * x) + "," + y + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6) + "V" + (2 * y - 6) + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y) + "Z" + "M" + (2.5 * x) + "," + (y + 8) + "V" + (2 * y - 8) + "M" + (4.5 * x) + "," + (y + 8) + "V" + (2 * y - 8);
        }
    
        chart.selectAll(".resize").append("path").attr("d", resizePath);
      });
      return value;
    }  
    e.onchange = onChange;
    service = onChange();

  


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


 
