/*
 * Sun path (Parabola) generator
 * ------------------------------------------------------------------
 * The `generateSunArc` function below draws a small arc that represents
 * the path of the sun between sunrise & sunset. It calculates points on
 * a unit semicircle, normalizes the current time between sunrise/sunset,
 * and places a marker where the sun currently is.
 *
 * Important: This is a geometric representation, not a physically
 * accurate astronomical model. It's primarily intended as a compact
 * visual indication for the UI.
 */
function parseTimeToDecimal(timeString) {
    // Accepts either 'HH:MM' or decimal hours like '6.5' and returns a number
    // representing the hours as decimal, e.g., '06:30' => 6.5. Returns null
    // for invalid inputs.
    if (!timeString) return null;
    if (timeString.includes(':')) {
        const parts = timeString.split(':');
        const h = parseInt(parts[0], 10);
        const m = parseInt(parts[1], 10);
        return h + m / 60;
    }
    // fallback: parse decimal
    return parseFloat(timeString);
}

let defaultSunrise = 6.5;
let defaultSunset = 18.5;
let defaultCurrent = (new Date()).getHours() + (new Date()).getMinutes() / 60;

/**
 * generateSunArc
 * - plotId: DOM id of the plot container (the Plotly graph div)
 * - containerId: container used to compute responsive width
 * - sunriseTime/sunsetTime: decimal hours (e.g., 06.5 for 06:30)
 * - currentTime: decimal hour that will be highlighted
 * - lineColor, markerColor: style customizations
 * - markerSymbol: Plotly marker symbol as fallback
 * - useFaIcon/faIconChar: attempt to render a FontAwesome glyph for the
 *   marker — Plotly will try to render a text trace; if unsupported, a
 *   regular marker is used.
 */
function generateSunArc(plotId, containerId, sunriseTime = defaultSunrise, sunsetTime = defaultSunset, currentTime = defaultCurrent, lineColor = 'orange', markerColor = 'red', markerSymbol = 'circle', useFaIcon = false, faIconChar = '\uF185') {
        if (typeof Plotly === 'undefined') {
            console.warn('Plotly is not loaded, skipping generateSunArc');
            return;
        }
        let xValues = [];
        let yValues = [];

        const sunriseAngle = Math.PI;
        const sunsetAngle = 0;
        let totalHours = sunsetTime - sunriseTime;
        if (!isFinite(totalHours) || totalHours <= 0) {
            // fallback to defaults if sunset <= sunrise
            totalHours = defaultSunset - defaultSunrise;
        }

        for(let h = sunriseTime; h <= sunsetTime; h += 0.1){
            let t = (h - sunriseTime) / totalHours;
            let angle = sunriseAngle * (1 - t);
            xValues.push(Math.cos(angle));
            yValues.push(Math.sin(angle));
        }

            // Helper to convert an hour value to x,y on the unit semicircle arc
        function timeToXY(hourValue) {
            let t = (hourValue - sunriseTime) / totalHours;
            if (t < 0) t = 0;
            if (t > 1) t = 1;
            const angle = sunriseAngle * (1 - t);
            return { x: Math.cos(angle), y: Math.sin(angle) };
        }

        // compute markers for sunrise/sunset and current time
        const sunrisePoint = timeToXY(sunriseTime);
        const sunsetPoint = timeToXY(sunsetTime);
        const currentPoint = timeToXY(currentTime);

        console.debug('generateSunArc debug', {plotId, sunriseTime, sunsetTime, currentTime, totalHours, sunrisePoint, sunsetPoint, currentPoint});

        // prevent errors if container missing – Plotly.react would otherwise throw
        if (!document.getElementById(plotId)) {
            console.warn('Plot container not found', plotId);
            return;
        }

        const traces = [
            {
                x: xValues,
                y: yValues,
                mode: 'lines',
                line: {color: lineColor, width: 3},
                    hoverinfo: "skip"
            },
            // sunrise marker
            {
                x: [sunrisePoint.x],
                y: [sunrisePoint.y],
                mode: 'markers',
                marker: {color: 'rgba(255,255,255,0.5)', size: 8, symbol: 'circle'},
                hoverinfo: 'skip'
            },
            // sunset marker
            {
                x: [sunsetPoint.x],
                y: [sunsetPoint.y],
                mode: 'markers',
                marker: {color: 'rgba(255,255,255,0.5)', size: 8, symbol: 'circle'},
                hoverinfo: 'skip'
            },
        ];

        // Optional: use FontAwesome icon for the marker if requested — fallback to regular marker
        if (useFaIcon) {
            // Add the FA icon as a text trace (requires FontAwesome CSS to be loaded)
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

        // Automatic range and padding
        let maxY = Math.max(...yValues, currentPoint.y);
        let padding = 0.15;

        // Responsive: width based on container
        const width = document.getElementById(containerId) ? document.getElementById(containerId).offsetWidth : 160;
        // make plot more visible by default
        const height = Math.max(90, Math.round(width * 0.75));
        console.debug('plot dims', { width, height });

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
            margin: {l:0, r:0, t:0, b:0},
            width: width,
            height: height,
            showlegend: false
            ,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };

        // Render the plot as static: no zoom/pan interactions or mode bar
        const plotlyConfig = { responsive: false, staticPlot: true, displayModeBar: false };
        Plotly.react(plotId, traces, layout, plotlyConfig);
}

// Make the function available globally
window.generateSunArc = generateSunArc;

function generatePlot() {
    // generatePlot() reads current sunrise/sunset values from the DOM and
    // converts them to decimals using `parseTimeToDecimal`. If fields are
    // missing, default values are used; then a call to generateSunArc() will
    // draw the arc in the 'sunArcPlot' placeholder.
    const sunriseEl = document.getElementById('sunrise');
    const sunsetEl = document.getElementById('sunset');
    const sunriseValParsed = sunriseEl ? parseTimeToDecimal((sunriseEl.innerText || sunriseEl.textContent).trim()) : null;
    const sunsetValParsed = sunsetEl ? parseTimeToDecimal((sunsetEl.innerText || sunsetEl.textContent).trim()) : null;
    const sunriseVal = (typeof sunriseValParsed === 'number' && !isNaN(sunriseValParsed)) ? sunriseValParsed : defaultSunrise;
    const sunsetVal = (typeof sunsetValParsed === 'number' && !isNaN(sunsetValParsed)) ? sunsetValParsed : defaultSunset;
    const now = new Date();
    const currentVal = now.getHours() + now.getMinutes() / 60;
    console.debug('generatePlot: sunriseVal, sunsetVal, currentVal', sunriseVal, sunsetVal, currentVal);

    // Render the combined sun arc block, if present
    if (document.getElementById('sunArcPlot')) {
        generateSunArc('sunArcPlot', 'sunArcPlot', sunriseVal, sunsetVal, currentVal, 'goldenrod', '#ffdf5f', 'star', true, '\uF185');
    }
}

// Export helper and hookup for resizing
window.generatePlot = generatePlot;
generatePlot();
window.addEventListener('resize', generatePlot);