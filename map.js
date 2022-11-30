const colori = [
    ["#b2df8a", "#33a02c", "#195016"],  // 0 verde
    ["#cab2d6", "#6a3d9a", "#351e4d"],  // 1 viola
    ["#a6cee3", "#1f78b4", "#0f3c59"],  // 2 blu-azzurro
    ["#fdbf6f", "#b15928", "#582c14"],  // 3 marrone-beige
    ["#fb9a99", "#e31a1c", "#710c0e"],  // 4 rosso-rosa
    ["#ffff99", "#df7f00", "#bb3f00"],  // 5 arancione-giallo
]

const prov_col = {
    "AG": 0,
    "AL": 0,
    "AN": 0,
    "AO": 1,
    "AP": 4,
    "AQ": 5,
    "AR": 0,
    "AT": 1,
    "AV": 2,
    "BA": 1,
    "BG": 4,
    "BI": 2,
    "BL": 0,
    "BN": 1,
    "BO": 2,
    "BR": 3,
    "BS": 1,
    "BT": 5,
    "BZ": 1,
    "CA": 1,
    "CB": 2,
    "CE": 0,
    "CH": 0,
    "CL": 2,
    "CN": 0,
    "CO": 0,
    "CR": 2,
    "CS": 3,
    "CT": 4,
    "CZ": 2,
    "EN": 0,
    "FC": 1,
    "FE": 0,
    "FG": 3,
    "FI": 2,
    "FM": 5,
    "FR": 2,
    "GE": 2,
    "GO": 3,
    "GR": 0,
    "IM": 4,
    "IS": 4,
    "KR": 0,
    "LC": 5,
    "LE": 2,
    "LI": 3,
    "LO": 3,
    "LT": 5,
    "LU": 0,
    "MB": 1,
    "MC": 2,
    "ME": 3,
    "MI": 2,
    "MN": 5,
    "MO": 1,
    "MS": 5,
    "MT": 2,
    "NA": 3,
    "NO": 4,
    "NU": 5,
    "OR": 0,
    "PA": 1,
    "PC": 5,
    "PD": 3,
    "PE": 4,
    "PG": 1,
    "PI": 1,
    "PN": 1,
    "PO": 5,
    "PR": 3,
    "PT": 4,
    "PU": 5,
    "PV": 1,
    "PZ": 0,
    "RA": 3,
    "RC": 0,
    "RE": 4,
    "RG": 5,
    "RI": 0,
    "RM": 1,
    "RN": 2,
    "RO": 4,
    "SA": 4,
    "SI": 4,
    "SO": 0,
    "SP": 1,
    "SR": 2,
    "SS": 2,
    "SU": 4,
    "SV": 5,
    "TA": 0,
    "TE": 1,
    "TN": 2,
    "TO": 3,
    "TP": 4,
    "TR": 5,
    "TS": 0,
    "TV": 4,
    "UD": 2,
    "VA": 3,
    "VB": 0,
    "VC": 5,
    "VE": 0,
    "VI": 1,
    "VR": 0,
    "VT": 3,
    "VV": 4,
};
const paintMap = () => {
    // create a tooltip
    const tooltip = d3.select("#container")
        .append("div")
        .style("position", "absolute")
        .style("opacity", 0)
        .style("filter", "drop-shadow(0 4px 3px rgb(0 0 0 / 0.07)) drop-shadow(0 2px 2px rgb(0 0 0 / 0.06))")
        .style("border-radius", "0.25rem")
        .style("padding", "0.25rem")
        .style("background-color", "rgba(255, 255, 255, 0.9)")
        .text("Tooltip");

    const width = 900, height = 700;
    const pathGenerator = d3.geoPath();
    const projection = d3.geoTransverseMercator()
        .center([8.689, 42.550]) // Center on Italy, adjusted for projection
        .scale(3800)
        .translate([width / 2 - 50, height / 2]);

    pathGenerator.projection(projection); // Assign projection to path object

    // Create the SVG that will contain our map
    const svg = d3.select('#chart').append("svg")
        .attr("id", "svg")
        .attr("width", width)
        .attr("height", height)
    // Append the group that will contain our paths
    const deps = svg.append("g");

    d3.json("capoluoghi.topo.json").then((tdata) => {
        const geo_shapes = topojson.feature(tdata, tdata.objects.comuni);
        var features = deps
            .selectAll("path")
            .data(geo_shapes.features)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .style("fill", (d) => colori[prov_col[d.properties.np]][d.properties.p ? 2 : (d.properties.c  ? 0 : 1)])
            .on("mouseover", function (event, d) {
                tooltip.transition().duration(200).style("opacity", 0.9);
                tooltip
                    .html(`Comune: <strong>${d.properties.n}</strong><br/>
                          Diventa: <strong>${d.properties.np}</strong><br/>
                          Era: <strong>${d.properties.op}</strong>`)
                    .style("left", event.pageX + 30 + "px")
                    .style("top", event.pageY - 30 + "px")
            })
            .on("mouseout", function (d) {
                tooltip.transition().duration(500).style("opacity", 0).end().then(() => tooltip.style("left", "-1000px").style("top", "-1000px")).catch(console.log);
            });
    })

    var zoom = d3.zoom()
        .scaleExtent([1, 10])
        .on('zoom', function (event) {
            deps.selectAll('path')
                .attr('transform', event.transform);
        });

    svg.call(zoom);


    d3.select('#zoom-in').on('click', function () {
        zoom.scaleBy(svg.transition().duration(50), 1.3);
    });
    d3.select('#zoom-zero').on('click', function () {
        zoom.scaleTo(svg.transition().duration(50), 1);
    });
    d3.select('#zoom-out').on('click', function () {
        zoom.scaleBy(svg.transition().duration(50), 1 / 1.3);
    });

};

document.addEventListener("DOMContentLoaded", paintMap);