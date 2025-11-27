// Beispiel-Daten: X = Zeitpunkte, Y = Temperaturwerte
let xValues = ["2025-11-27 08:00", "2025-11-27 09:00", "2025-11-27 10:00"];
let yValues = [20, 21, 22]; // Diese Werte könnten aus einer Variable kommen

// Optional: Funktion zum dynamischen Update von Werten
function updatePlot(newX, newY) {
    Plotly.update("weatherPlot", {x:[newX], y:[newY]});
}

// Erstellen des Diagramms
const trace = {
    x: xValues,
    y: yValues,
    mode: "lines+markers",
    name: "Temperatur (°C)"
};

const layout = {
    title: "Temperaturverlauf",
    xaxis: {title: "Zeit"},
    yaxis: {title: "Temperatur (°C)"}
};

Plotly.newPlot("weatherPlot", [trace], layout);

// Beispiel: neue Daten nach 3 Sekunden pushen
setTimeout(() => {
    let newX = ["2025-11-27 11:00"];
    let newY = [23];
    xValues.push(...newX);
    yValues.push(...newY);
    updatePlot(xValues, yValues);
}, 3000);


//Sonnenaufgang
let sunriseTime = 6.5;
    let sunsetTime = 18.5;
    let currentTime = 18.5;

    function generatePlot() {
        let xValues = [];
        let yValues = [];

        const sunriseAngle = Math.PI;
        const sunsetAngle = 0;
        const totalHours = sunsetTime - sunriseTime;

        for(let h = sunriseTime; h <= sunsetTime; h += 0.1){
            let t = (h - sunriseTime) / totalHours;
            let angle = sunriseAngle * (1 - t);
            xValues.push(Math.cos(angle));
            yValues.push(Math.sin(angle));
        }

        // Aktuelle Zeit → Punkt
        let tCur = (currentTime - sunriseTime) / totalHours;
        let curAngle = sunriseAngle * (1 - tCur);
        let curX = Math.cos(curAngle);
        let curY = Math.sin(curAngle);

        const traces = [
            {
                x: xValues,
                y: yValues,
                mode: 'lines',
                line: {color: 'orange', width: 3},
                hoverinfo: "none"
            },
            {
                x: [curX],
                y: [curY],
                mode: 'markers',
                marker: {color: 'red', size: 14},
                hoverinfo: "none"
            }
        ];

        // ⬆️ NEU: AUTOMATISCHE RANGE, damit Punkt NIE abgeschnitten wird
        let maxY = Math.max(...yValues, curY);
        let padding = 0.15; 

        // Responsive Größe
        const width = document.getElementById("sunCircleContainer").offsetWidth;
        const height = width * 0.8;

        const layout = {
            xaxis: {
                showgrid: false,
                zeroline: false,
                showticklabels: false,
                range: [-1.2, 1.2]
            },
            yaxis: {
                showgrid: false,
                zeroline: false,
                showticklabels: false,
                range: [-0.1, maxY + padding],
                scaleanchor: "x"
            },
            margin: {l:0, r:0, t:40, b:0},
            width: width,
            height: height,
            showlegend: false
        };

        Plotly.newPlot("sunCircle", traces, layout, {responsive: false});
    }

    generatePlot();
    window.addEventListener("resize", generatePlot);