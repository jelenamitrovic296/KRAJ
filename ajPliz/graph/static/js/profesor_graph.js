// static/js/profesor_graph.js

function ucitajGrafProfesor(podaci) {

    const tree = d3.select("#tree");
    const tooltip = d3.select("#tooltip");

    if (!podaci || !podaci.cvorovi || !podaci.veze) {
        console.error("Neispravni podaci za graf profesora:", podaci);
        return;
    }

    tree.selectAll("*").remove();

    const sirina = 4000;
    const visina = 3500;

    const svg = tree.append("svg")
        .attr("width", sirina)
        .attr("height", visina);


    const simulacija = d3.forceSimulation(podaci.cvorovi)
        .force(
            "link",
            d3.forceLink(podaci.veze)
                .id(d => d.id)
                .distance(80)
        )
        .force("charge", d3.forceManyBody().strength(-800))
        .force("center", d3.forceCenter(sirina / 2, visina / 2))
        .force("collision", d3.forceCollide().radius(80));

    // ================= VEZE =================

    const link = svg.selectAll(".link")
        .data(podaci.veze)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke-width", 1)
        .attr("stroke", d => {
            if (d.tip === "master") return "orange";
            if (d.tip === "doktorska") return "purple";
            return "gray";
        });

    // ================= ČVOROVI =================

    const node = svg.selectAll(".node")
        .data(podaci.cvorovi)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(
            d3.drag()
                .on("start", dragStart)
                .on("drag", dragging)
                .on("end", dragEnd)
        );

    node.append("circle")
        .attr("r", 10)
        .attr("fill", d => {
            if (d.grupa === 1) return "red";      // mentorstvo
            if (d.grupa === 2) return "blue";     // komisija
            return "gray";                        // profesor
        })
      .on("click", (event, d) => {
    const delovi = d.id.split(" ");
    const ime = delovi[0];
    const prezime = delovi.slice(1).join(" ");

    if (d.grupa === 0) {
        // Profesor
        if (typeof prikaziStatistiku === "function") {
            prikaziStatistiku(ime, prezime);
        }
    } else {
        // Student - proveravamo svako moguće polje za naslov
        if (typeof prikaziGraf === "function") {
            const naslov = d.naslov || 
                          d.naslov_master_rad || 
                          d.naslov_doktorske_teze || 
                          ""; // Ako ništa ne nađe, šalje prazan string

            console.log("Pronađen naslov:", naslov);
            prikaziGraf(ime, prezime, naslov);
        }
    }
})
        .on("mouseover", (event, d) => {
            tooltip
                .style("visibility", "visible")
                .html(`
                    <strong>${d.id}</strong><br>
                    ${d.smer ? `Смер: ${d.smer}<br>` : ""}
                    ${d.naslov_master_rad ? `Наслов мастер рада: ${d.naslov_master_rad}<br>` : ""}
                    ${d.godina_odbrane_master_rad ? `Година одбране мастер рада: ${d.godina_odbrane_master_rad}<br>` : ""}
                    ${d.naslov_doktorske_teze ? `Назив докторске дисертације: ${d.naslov_doktorske_teze}<br>` : ""}
                    ${d.godina_odbrane_doktorske_teze ? `Година одбране докторске дисертације: ${d.godina_odbrane_doktorske_teze}<br>` : ""}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px");
        })
        .on("mousemove", (event) => {
            tooltip
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px");
        })
        .on("mouseout", () => {
            tooltip.style("visibility", "hidden");
        });

    node.append("text")
        .attr("dy", 20)
        .style("text-anchor", "middle")
        .style("font-size", "12px")
        .text(d => d.id);

    // ================= TICK =================

    simulacija.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", d => `translate(${d.x}, ${d.y})`);
    });

    // ================= DRAG FUNKCIJE =================

    function dragStart(event, d) {
        if (!event.active) simulacija.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragging(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnd(event, d) {
        if (!event.active) simulacija.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {
  // const meni = document.getElementById("meni");
  // meni.style.display = "none";
    if (typeof grafPodaciProfesor !== "undefined") {
        ucitajGrafProfesor(grafPodaciProfesor);
    } else {
        console.error("grafPodaciProfesor nije definisan");
    }
});
