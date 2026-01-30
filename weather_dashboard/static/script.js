/*
 * Sonnenbahn-Visualisierung (Sun Arc Generator)
 * Zeichnet einen Bogen, der den Weg der Sonne zwischen
 * Auf- und Untergang darstellt. Geometrische Darstellung,
 * keine astronomisch exakte Berechnung.
 */

/**
 * parseTimeToDecimal
 * Konvertiert Zeit-String in Dezimalstunden
 * '06:30' → 6.5 oder '6.5' → 6.5
 */
function parseTimeToDecimal(timeString) {
    if (!timeString) return null;
    if (timeString.includes(':')) {
        const parts = timeString.split(':');
        const h = parseInt(parts[0], 10);
        const m = parseInt(parts[1], 10);
        return h + m / 60;
    }
    // Fallback: Parse als Dezimalzahl
    return parseFloat(timeString);
}

let defaultSunrise = 6.5;
let defaultSunset = 18.5;
let defaultCurrent = (new Date()).getHours() + (new Date()).getMinutes() / 60;

/**
 * generateSunArc - Zeichnet Sonnenbahn mit Plotly
 * Berechnet Bogen zwischen Sonnenauf- und -untergang
 * und platziert aktuellen Sonnenstand als Marker
 */
function generateSunArc(plotId, containerId, sunriseTime = defaultSunrise, sunsetTime = defaultSunset, currentTime = defaultCurrent, lineColor = 'orange', markerColor = 'red', markerSymbol = 'circle', useFaIcon = false, faIconChar = '\uF185') {
        if (typeof Plotly === 'undefined') {
            console.warn('Plotly nicht geladen, generateSunArc übersprungen');
            return;
        }
        let xValues = [];
        let yValues = [];

        const sunriseAngle = Math.PI;
        const sunsetAngle = 0;
        let totalHours = sunsetTime - sunriseTime;
        if (!isFinite(totalHours) || totalHours <= 0) {
            // Fallback auf Standardwerte falls Sonnenuntergang <= Sonnenaufgang
            totalHours = defaultSunset - defaultSunrise;
        }

        // Berechne Punkte auf dem Halbkreis-Bogen
        for(let h = sunriseTime; h <= sunsetTime; h += 0.1){
            let t = (h - sunriseTime) / totalHours;
            let angle = sunriseAngle * (1 - t);
            xValues.push(Math.cos(angle));
            yValues.push(Math.sin(angle) * 0.75); // Vertikale Kompression
        }

        // Hilfsfunktion: Konvertiere Stundenwert zu x,y Koordinaten
        function timeToXY(hourValue) {
            let t = (hourValue - sunriseTime) / totalHours;
            if (t < 0) t = 0;
            if (t > 1) t = 1;
            const angle = sunriseAngle * (1 - t);
            return { x: Math.cos(angle), y: Math.sin(angle) * 0.75 };
        }

        // Berechne Positionen: Aufgang, Untergang, aktuelle Zeit
        const sunrisePoint = timeToXY(sunriseTime);
        const sunsetPoint = timeToXY(sunsetTime);
        const currentPoint = timeToXY(currentTime);



        // Fehlerbehandlung: Container muss existieren
        if (!document.getElementById(plotId)) {
            console.warn('Plot-Container nicht gefunden:', plotId);
            return;
        }

        // Erstelle Plotly Traces: Bogen + Marker
        const traces = [
            // Sonnenbahn-Linie
            {
                x: xValues,
                y: yValues,
                mode: 'lines',
                line: {color: lineColor, width: 3},
                hoverinfo: "skip"
            },
            // Sonnenaufgang-Marker
            {
                x: [sunrisePoint.x],
                y: [sunrisePoint.y],
                mode: 'markers',
                marker: {color: 'rgba(255,255,255,0.5)', size: 8, symbol: 'circle'},
                hoverinfo: 'skip'
            },
            // Sonnenuntergang-Marker
            {
                x: [sunsetPoint.x],
                y: [sunsetPoint.y],
                mode: 'markers',
                marker: {color: 'rgba(255,255,255,0.5)', size: 8, symbol: 'circle'},
                hoverinfo: 'skip'
            },
        ];

        // Aktuelle Sonnenposition-Marker
        if (useFaIcon) {
            // Versuche FontAwesome-Icon als Text Trace (benötigt geladenes FontAwesome CSS)
            traces.push({
                x: [currentPoint.x],
                y: [currentPoint.y],
                mode: 'markers',
                marker: { color: markerColor, size: 18 },
                hoverinfo: 'skip'
            });
        } else {
            traces.push({
                x: [currentPoint.x],
                y: [currentPoint.y],
                mode: 'markers',
                marker: {color: markerColor, size: 18 },
                hoverinfo: 'skip'
            });
        }

        // Automatische Bereich- und Padding-Berechnung
        let maxY = Math.max(...yValues, currentPoint.y);
        let padding = 0.15;

        // Responsive: Breite basierend auf Container
        const width = document.getElementById(containerId) ? document.getElementById(containerId).offsetWidth : 160;
        const height = Math.max(150, Math.round(width * 0.75));
        console.debug('Plot-Dimensionen:', { width, height });

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
                range: [0, maxY + padding],
                scaleanchor: "x"
            },
            margin: {l:0, r:0, t:0, b:0},
            width: width,
            height: height,
            showlegend: false,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };

        // Render als statischer Plot: keine Zoom/Pan-Interaktionen oder Mode Bar
        const plotlyConfig = { responsive: false, staticPlot: true, displayModeBar: false };
        Plotly.react(plotId, traces, layout, plotlyConfig);
}

// Globale Verfügbarkeit der Funktion
window.generateSunArc = generateSunArc;

/**
 * generatePlot - Rendere Sonnenbahn-Block neu
 * Liest Auf-/Untergangszeiten aus DOM und zeigt aktuellen Sonnenstand
 */
function generatePlot() {
    const sunriseEl = document.getElementById('sunrise');
    const sunsetEl = document.getElementById('sunset');
    const sunriseValParsed = sunriseEl ? parseTimeToDecimal((sunriseEl.innerText || sunriseEl.textContent).trim()) : null;
    const sunsetValParsed = sunsetEl ? parseTimeToDecimal((sunsetEl.innerText || sunsetEl.textContent).trim()) : null;
    const sunriseVal = (typeof sunriseValParsed === 'number' && !isNaN(sunriseValParsed)) ? sunriseValParsed : defaultSunrise;
    const sunsetVal = (typeof sunsetValParsed === 'number' && !isNaN(sunsetValParsed)) ? sunsetValParsed : defaultSunset;
    const now = new Date();
    const currentVal = now.getHours() + now.getMinutes() / 60;
    console.debug('Plot: Aufgang, Untergang, aktuell:', sunriseVal, sunsetVal, currentVal);

    // Render kombinierter Sonnenbahn-Block, falls vorhanden
    if (document.getElementById('sunArcPlot')) {
        generateSunArc('sunArcPlot', 'sunArcPlot', sunriseVal, sunsetVal, currentVal, 'goldenrod', '#ffdf5f', 'star', true, '\uF185');
    }
}

// Export der Funktion und Hookup für Größenänderungen
window.generatePlot = generatePlot;
generatePlot();
window.addEventListener('resize', generatePlot);