// static/js/student_graph.js

function ucitajGraf(podaciStablo) {
    const parametriUrl = new URLSearchParams(window.location.search);
    const ime = parametriUrl.get('ime_studenta');
    const prezime = parametriUrl.get('prezime_studenta');
    var ispisPodataka = d3.select("#tooltip");
    
    if (ime && prezime && podaciStablo) {
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
                if (d.target.data.veza === "mentor_master_rad") {
                    return "Ментор мастер рада";
                } else if (d.target.data.veza === "mentor_doktorska_teza") {
                    return "Ментор докторске дисертације";
                } else if (d.target.data.veza === "komisija_master_rad") {
                    return "Члан комисије мастер рада";
                } else if (d.target.data.veza === "komisija_doktorska_teza") {
                    return "Члан комисије докторске дисертације";
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
                    const [ime, prezime] = d.data.ime.split(" ");
                    console.log("ime_prezime", ime, prezime);
                    prikaziStatistiku(ime, prezime);
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
            .attr("dx", d => d.depth === 0 ? 0 : 0)
            .attr("dy", d => d.depth === 0 ? -18 : -20)
            .style("font-size", d => d.depth === 0 ? "16px" : "13px")
            .style("text-anchor", "middle")
            .html(d => `${d.data.ime}`);
    }
}

// Funkcija koja se poziva na učitavanje stranice
function initGraf() {
    // Podaci će biti prosleđeni iz Django template-a
    if (typeof grafPodaci !== 'undefined' && grafPodaci) {
        ucitajGraf(grafPodaci);
    }
}

// Inicijalizacija kad se učita DOM
document.addEventListener('DOMContentLoaded', initGraf);
