// // charts
// let tempChart = null
// let humidityChart = null
// let moistureChart = null


// // ---------------- GAUGE DRAW FUNCTION ----------------

// function drawGauge(chartRef, canvasId, value, max, color){

// const ctx = document.getElementById(canvasId)

// if(!ctx) return chartRef

// // destroy old chart to prevent stacking
// if(chartRef){
// chartRef.destroy()
// }

// chartRef = new Chart(ctx, {

// type: "doughnut",

// data: {
// datasets: [{
// data: [value, max - value],
// backgroundColor: [color, "#e5e7eb"],
// borderWidth: 0
// }]
// },

// options: {

// responsive: true,
// maintainAspectRatio: false,

// rotation: -90,
// circumference: 180,

// cutout: "65%",

// plugins: {
// legend: { display: false },
// tooltip: { enabled: false }
// }

// }

// })

// return chartRef
// }



// // ---------------- LOAD SENSOR DATA ----------------

// async function loadSensors(){

// try{

// let r = await fetch("/api/thingspeak")
// let data = await r.json()

// let feeds = data.feeds

// if(!feeds || feeds.length === 0) return

// let last = feeds[feeds.length - 1]

// let moisture = parseFloat(last.field1)
// let temp = parseFloat(last.field2)
// let humidity = parseFloat(last.field3)
// // Temperature arrow
// let tempArrow = document.getElementById("tempArrow")
// if(temp < 28){
// tempArrow.innerHTML = " ↓"
// tempArrow.style.color = "blue"
// }
// else if(temp > 32){
// tempArrow.innerHTML = " ↑"
// tempArrow.style.color = "red"
// }
// else{
// tempArrow.innerHTML = " ✔"
// tempArrow.style.color = "green"
// }


// // Humidity arrow
// let humArrow = document.getElementById("humidityArrow")
// if(humidity < 36){
// humArrow.innerHTML = " ↓"
// humArrow.style.color = "orange"
// }
// else if(humidity > 45){
// humArrow.innerHTML = " ↑"
// humArrow.style.color = "red"
// }
// else{
// humArrow.innerHTML = " ✔"
// humArrow.style.color = "green"
// }


// // Moisture arrow
// let moistArrow = document.getElementById("moistureArrow")
// if(moisture < 28){
// moistArrow.innerHTML = " ↓"
// moistArrow.style.color = "orange"
// }
// else if(moisture > 36){
// moistArrow.innerHTML = " ↑"
// moistArrow.style.color = "blue"
// }
// else{
// moistArrow.innerHTML = " ✔"
// moistArrow.style.color = "green"
// }
// // update values inside gauges

// const tempEl = document.getElementById("tempValue")
// if(tempEl) tempEl.innerHTML = temp.toFixed(1) + "°C"

// const humEl = document.getElementById("humidityValue")
// if(humEl) humEl.innerHTML = humidity.toFixed(1) + "%"

// const moistEl = document.getElementById("moistureValue")
// if(moistEl) moistEl.innerHTML = moisture.toFixed(1) + "%"


// // draw gauges

// tempChart = drawGauge(tempChart,"tempGauge",temp,50,"#3b82f6")

// humidityChart = drawGauge(humidityChart,"humidityGauge",humidity,100,"#ef4444")

// moistureChart = drawGauge(moistureChart,"moistureGauge",moisture,100,"#22c55e")

// }catch(err){

// console.log("Sensor API error:",err)

// }

// }



// // ---------------- GROWTH COMPARISON ----------------

// async function loadGrowthComparison(){

// try{

// let r = await fetch("/api/growth_comparison")
// let data = await r.json()

// document.getElementById("greenhouseGrowth").innerHTML =
// "<i class='fas fa-arrow-up text-success'></i> " +
// data.greenhouse_avg.toFixed(2) + "%"

// document.getElementById("outdoorGrowth").innerHTML =
// "<i class='fas fa-arrow-down text-danger'></i> " +
// data.outdoor_avg.toFixed(2) + "%"

// document.getElementById("growthDiff").innerHTML =
// "<i class='fas fa-arrow-up text-success'></i> +" +
// data.improvement.toFixed(2) + "%"

// }catch(err){

// console.log("Growth API error:",err)

// }

// }



// // ---------------- INITIAL LOAD ----------------

// loadSensors()
// loadGrowthComparison()


// // ---------------- AUTO REFRESH ----------------

// setInterval(loadSensors,15000)

// setInterval(loadGrowthComparison,60000)




// ---------------- GLOBAL CHART REFS ----------------
let tempChart = null
let humidityChart = null
let moistureChart = null

let growthLoaded = false   // for loader control


// ---------------- GAUGE DRAW FUNCTION ----------------
function drawGauge(chartRef, canvasId, value, max, color){

  const ctx = document.getElementById(canvasId)
  if(!ctx) return chartRef

  // destroy old chart to prevent stacking
  if(chartRef){
    chartRef.destroy()
  }

  return new Chart(ctx, {
    type: "doughnut",

    data: {
      datasets: [{
        data: [value, max - value],
        backgroundColor: [color, "#e5e7eb"],
        borderWidth: 0
      }]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      rotation: -90,
      circumference: 180,

      cutout: "65%",

      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  })
}


// ---------------- LOAD SENSOR DATA ----------------
async function loadSensors(){

  try{

    let r = await fetch("/api/thingspeak")
    let data = await r.json()

    let feeds = data.feeds
    if(!feeds || feeds.length === 0) return

    let last = feeds[feeds.length - 1]

    let moisture = parseFloat(last.field1) || 0
    let temp = parseFloat(last.field2) || 0
    let humidity = parseFloat(last.field3) || 0


    // -------- TEMPERATURE ARROW --------
    let tempArrow = document.getElementById("tempArrow")
    if(tempArrow){
      if(temp < 28){
        tempArrow.innerHTML = " ↓"
        tempArrow.style.color = "blue"
      }
      else if(temp > 32){
        tempArrow.innerHTML = " ↑"
        tempArrow.style.color = "red"
      }
      else{
        tempArrow.innerHTML = " ✔"
        tempArrow.style.color = "green"
      }
    }


    // -------- HUMIDITY ARROW --------
    let humArrow = document.getElementById("humidityArrow")
    if(humArrow){
      if(humidity < 36){
        humArrow.innerHTML = " ↓"
        humArrow.style.color = "orange"
      }
      else if(humidity > 45){
        humArrow.innerHTML = " ↑"
        humArrow.style.color = "red"
      }
      else{
        humArrow.innerHTML = " ✔"
        humArrow.style.color = "green"
      }
    }


    // -------- MOISTURE ARROW --------
    let moistArrow = document.getElementById("moistureArrow")
    if(moistArrow){
      if(moisture < 28){
        moistArrow.innerHTML = " ↓"
        moistArrow.style.color = "orange"
      }
      else if(moisture > 36){
        moistArrow.innerHTML = " ↑"
        moistArrow.style.color = "blue"
      }
      else{
        moistArrow.innerHTML = " ✔"
        moistArrow.style.color = "green"
      }
    }


    // -------- UPDATE VALUES --------
    const tempEl = document.getElementById("tempValue")
    if(tempEl) tempEl.innerHTML = temp.toFixed(1) + "°C"

    const humEl = document.getElementById("humidityValue")
    if(humEl) humEl.innerHTML = humidity.toFixed(1) + "%"

    const moistEl = document.getElementById("moistureValue")
    if(moistEl) moistEl.innerHTML = moisture.toFixed(1) + "%"


    // -------- DRAW GAUGES --------
    tempChart = drawGauge(tempChart, "tempGauge", temp, 50, "#3b82f6")
    humidityChart = drawGauge(humidityChart, "humidityGauge", humidity, 100, "#ef4444")
    moistureChart = drawGauge(moistureChart, "moistureGauge", moisture, 100, "#22c55e")

  }catch(err){
    console.log("Sensor API error:", err)
  }
}



// ---------------- GROWTH COMPARISON ----------------
async function loadGrowthComparison(){

  try{

    // -------- SHOW LOADER ONLY FIRST TIME --------
    if(!growthLoaded){
      toggleGrowthLoader(true)
    }

    let r = await fetch("/api/growth_comparison")
    let data = await r.json()


    // -------- UPDATE VALUES --------
    const greenhouse = document.getElementById("greenhouseGrowth")
    const outdoor = document.getElementById("outdoorGrowth")
    const diff = document.getElementById("growthDiff")

    if(greenhouse){
      greenhouse.innerHTML =
        "<i class='fas fa-arrow-up text-success'></i> " +
        data.greenhouse_avg.toFixed(2) + "%"
    }

    if(outdoor){
      outdoor.innerHTML =
        "<i class='fas fa-arrow-down text-danger'></i> " +
        data.outdoor_avg.toFixed(2) + "%"
    }

    if(diff){
      diff.innerHTML =
        "<i class='fas fa-arrow-up text-success'></i> +" +
        data.improvement.toFixed(2) + "%"
    }


    // -------- HIDE LOADER --------
    toggleGrowthLoader(false)

    growthLoaded = true

  }catch(err){
    console.log("Growth API error:", err)
  }

}



// ---------------- LOADER HELPER ----------------
function toggleGrowthLoader(show){

  const loaders = [
    document.getElementById("greenhouseLoader"),
    document.getElementById("outdoorLoader"),
    document.getElementById("diffLoader")
  ]

  const values = [
    document.getElementById("greenhouseGrowth"),
    document.getElementById("outdoorGrowth"),
    document.getElementById("growthDiff")
  ]

  loaders.forEach(el => {
    if(el) el.style.display = show ? "block" : "none"
  })

  values.forEach(el => {
    if(el) el.style.display = show ? "none" : "block"
  })
}



// ---------------- INITIAL LOAD ----------------
document.addEventListener("DOMContentLoaded", () => {
  loadSensors()
  loadGrowthComparison()
})


// ---------------- AUTO REFRESH ----------------
setInterval(loadSensors, 15000)        // every 15 sec
setInterval(loadGrowthComparison, 60000) // every 60 sec