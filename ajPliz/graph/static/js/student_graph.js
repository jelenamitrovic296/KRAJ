// static/js/student_graph.js

function ucitajGraf(podaciStablo) {
    // Provera da li postoje svi potrebni elementi
    const treeElement = document.getElementById("tree");
    const tooltipElement = document.getElementById("tooltip");
    
    if (!treeElement) {
        console.error("Element #tree ne postoji!");
        return;
    }
    
    if (!tooltipElement) {
        console.error("Element #tooltip ne postoji!");
        return;
    }
    
    if (!podaciStablo) {
        console.error("Nema podataka za graf!");
        return;
    }

    // Očisti prethodni SVG ako postoji
    d3.select("#tree").selectAll("*").remove();
    
    var ispisPodataka = d3.select("#tooltip");
    
    var margina = { gore: 30, desno: 30, dole: 30, levo: 30 },
        sirina = 1600 - margina.levo - margina.desno,
        visina = 800 - margina.gore - margina.dole;

    var svg = d3.select("#tree").append("svg")
        .attr("width", sirina + margina.levo + margina.desno)
        .attr("height", visina + margina.gore + margina.dole)
        .append("g")
        .attr("transform", "translate(" + margina.levo + "," + margina.desno + ")");

    var koren = d3.hierarchy(podaciStablo);
    var rasporediCvorove = d3.tree().size([sirina, visina]);

    rasporediCvorove(koren);
    
    // Veze
    svg.selectAll(".veza")
        .data(koren.links())
        .enter().append("line")
        .attr("class", "link")
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)
        .attr("stroke", "#999")
        .attr("stroke-width", 2);
        
    // Labele veza
    svg.selectAll(".veza-label")
        .data(koren.links())
        .enter().append("text")
        .attr("class", "veza-label")
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2)
        .style("text-anchor", "middle")
        .attr("transform", d => {
            const ugao = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x) * 180 / Math.PI;
            return `rotate(${ugao}, ${(d.source.x + d.target.x) / 2}, ${(d.source.y + d.target.y) / 2})`;
        })
        .text(d => {
            if (d.target.data.uloga === "mentor_master_rad") {
                return "Ментор";
            } else if (d.target.data.uloga === "mentor_doktorska_teza") {
                return "Ментор";
            } else if (d.target.data.uloga === "komisija_master_rad") {
                return "Члан комисије";
            } else if (d.target.data.uloga === "komisija_doktorska_teza") {
                return "Члан комисије";
            }
            return "";
        });

    // Čvorovi
    var cvorovi = svg.selectAll(".node")
        .data(koren.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x},${d.y})`);
        
    cvorovi.append("circle")
        .attr("r", 15)
        .attr("fill", d => {
            if (d.data.uloga === "mentor_master_rad" || d.data.uloga === "mentor_doktorska_teza") {
                return "red";
            } else if (d.data.uloga === "komisija_master_rad" || d.data.uloga === "komisija_doktorska_teza") {
                return "blue";
            } else if (d.data.uloga === "student") {
                return "gray";
            }
            return "orange";
        })
        .on("click", function(event, d) {
            if (d.data.grupa === 1) {
                const delovi = d.data.ime.trim().split(/\s+/);
                const ime = delovi[0];
                const prezime = delovi.slice(1).join(" ");
                console.log("ime_prezime", ime, prezime);
                if (typeof prikaziStatistiku === 'function') {
                    prikaziStatistiku(ime, prezime);
                }
            }
        })
        .on("mouseover", function(event, d) {
            ispisPodataka.style("visibility", "visible")
                .html(`
                    <strong>${d.data.ime}</strong><br>
                    ${d.data.uloga === "student" ? `
                        ${d.data.naslov_master_rada && d.data.naslov_master_rada !== "None" ? `Наслов мастер рада: ${d.data.naslov_master_rada}<br>` : ""}
                        ${d.data.godina_odbrane_master_rada && d.data.godina_odbrane_master_rada !== "None" ? `Година одбране мастер рада: ${d.data.godina_odbrane_master_rada}<br>` : ""}
                        ${d.data.naslov_doktorske_teze && d.data.naslov_doktorske_teze !== "None" ? `Наслов докторске дисертације: ${d.data.naslov_doktorske_teze}<br>` : ""}
                        ${d.data.godina_odbrane_doktorske_teze && d.data.godina_odbrane_doktorske_teze !== "None" ? `Година одбране докторске дисертације: ${d.data.godina_odbrane_doktorske_teze}` : ""}
                    ` : ""}
                    ${["mentor_master_rad", "mentor_doktorska_teza", "komisija_master_rad", "komisija_doktorska_teza"].includes(d.data.uloga) ? `
                        ${d.data.institucija ? `Институција: ${d.data.institucija}` : ""}
                    ` : ""}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px");
        })
        .on("mousemove", function(event) {
            ispisPodataka.style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px");
        })
        .on("mouseout", function() {
            ispisPodataka.style("visibility", "hidden");
        });
        
    cvorovi.append("text")
        .attr("dx", 0)
        .attr("pointer-events", "none")

        .attr("dy", d => d.depth === 0 ? -18 : -20)
        .style("font-size", d => d.depth === 0 ? "16px" : "13px")
        .style("text-anchor", "middle")
        .html(d => `${d.data.ime}`);
}

// Funkcija koja se poziva na učitavanje stranice
function initGraf() {
    console.log("initGraf pozvana");
    
    // Provera da li postoje podaci
    //const meni = document.getElementById("meni");
   // meni.style.display = "none";
    if (typeof grafPodaci !== 'undefined' && grafPodaci) {
        console.log("Podaci pronađeni:", grafPodaci);
        ucitajGraf(grafPodaci);
    } else {
        console.error("grafPodaci nije definisan!");
    }
}

// Inicijalizacija kad se učita DOM
document.addEventListener('DOMContentLoaded', initGraf);
