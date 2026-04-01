let charts = {}

async function loadData(){

// -------------------------
// SENSOR DATA FROM THINGSPEAK
// -------------------------

let r = await fetch("/api/thingspeak")
let data = await r.json()

let feeds = data.feeds

if(!feeds || feeds.length==0) return

feeds = feeds.slice(-10)

let last = feeds[feeds.length-1]

// update cards

document.getElementById("moisture").innerHTML =
(parseFloat(last.field1) || 0).toFixed(2) + " %"

document.getElementById("temp").innerHTML =
(parseFloat(last.field2) || 0).toFixed(1) + " °C"

document.getElementById("humidity").innerHTML =
(parseFloat(last.field3) || 0).toFixed(1) + " %"

document.getElementById("pump").innerHTML =
(parseFloat(last.field4) || 0).toFixed(2) + " sec"

document.getElementById("fan").innerHTML =
(parseFloat(last.field5) || 0) ? "OFF" : "OFF"

document.getElementById("dry").innerHTML =
(parseFloat(last.field6) || 0).toFixed(2)


// -------------------------
// PREDICTION DATA
// -------------------------

let irr = await fetch("/api/irrigation")
let irr_data = await irr.json()

if(document.getElementById("next_runtime")){

document.getElementById("next_runtime").innerHTML =
(irr_data.next_runtime || 0).toFixed(2) + " sec"

}

if(document.getElementById("next_water")){

document.getElementById("next_water").innerHTML =
(irr_data.next_volume || 0).toFixed(2) + " ml"

}


// -------------------------
// CHART DATA
// -------------------------

let labels=[]
let moisture=[]
let temp=[]
let humidity=[]
let pump=[]
let fan=[]

feeds.forEach(f => {

labels.push(new Date(f.created_at).toLocaleTimeString())

moisture.push(parseFloat(f.field1) || 0)
temp.push(parseFloat(f.field2) || 0)
humidity.push(parseFloat(f.field3) || 0)
pump.push(parseFloat(f.field4) || 0)
fan.push(parseFloat(f.field5) || 0)

})


createChart("chart_moisture","Moisture",labels,moisture)
createChart("chart_temp","Temperature",labels,temp)
createChart("chart_humidity","Humidity",labels,humidity)
createChart("chart_pump","Pump",labels,pump)
createChart("chart_fan","Fan",labels,fan)

}


// -------------------------
// CHART FUNCTION
// -------------------------

function createChart(id,label,labels,data){

if(!document.getElementById(id)) return

if(charts[id]) charts[id].destroy()

charts[id] = new Chart(document.getElementById(id),{

type:"line",

data:{
labels:labels,
datasets:[{
label:label,
data:data,
tension:0.3
}]
},

options:{
responsive:true,
plugins:{
legend:{display:false}
}
}

})

}


loadData()

setInterval(loadData,15000)