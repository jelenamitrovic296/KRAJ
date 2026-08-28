document.addEventListener("DOMContentLoaded", () => {
    ucitajGraf();
});
function ucitajGraf() {
    const podaci = window.STUDENTSKI_GRAF_PODACI;
    const ispisPodataka = d3.select("#tooltip");
    const postojeciCvorovi = new Set();
    podaci.cvorovi = podaci.cvorovi.filter(c => {
        if (postojeciCvorovi.has(c.id)) return false;
        postojeciCvorovi.add(c.id);
        return true;
    });
    const sirina = 4000;
    const visina = 3500;
    const svg = d3.select("#tree")
        .append("svg")
        .attr("width", sirina)
        .attr("height", visina);
    // LEGENDA
    const legenda = svg.append("g")
        .attr("transform", "translate(100,100)");
    const legendaPodaci = [
        { label: "Професор ментор", color: "red" },
        { label: "Професор члан комисије", color: "blue" },
        { label: "Студент", color: "gray" }
    ];
    legenda.selectAll("rect")
        .data(legendaPodaci)
        .enter()
        .append("rect")
        .attr("y", (d, i) => i * 25)
        .attr("width", 20)
        .attr("height", 20)
        .attr("fill", d => d.color);
    legenda.selectAll("text")
        .data(legendaPodaci)
        .enter()
        .append("text")
        .attr("x", 30)
        .attr("y", (d, i) => i * 25 + 15)
        .text(d => d.label);
    const simulacija = d3.forceSimulation(podaci.cvorovi)
        .force("link", d3.forceLink(podaci.veze).id(d => d.id).distance(50))
        .force("charge", d3.forceManyBody().strength(-60))
        .force("center", d3.forceCenter(sirina / 2, visina / 2))
        .force("collision", d3.forceCollide().radius(68));
    const link = svg.selectAll(".link")
        .data(podaci.veze)
        .enter()
        .append("line")
        .attr("stroke", "#999");
    const cvor = svg.selectAll(".node")
        .data(podaci.cvorovi)
        .enter()
        .append("g")
        .call(d3.drag()
            .on("start", zapocniPovlacenje)
            .on("drag", povlacenje)
            .on("end", zavrsiPovlacenje)
        );
    cvor.append("circle")
        .attr("r", 10)
        .attr("fill", d =>
            d.uloga === "mentor" ? "red" :
            d.uloga === "clan_komisije" ? "blue" : "gray"
        )
        .on("click", (event, d) => {
            if (d.uloga === "student") {
                const [ime, prezime] = d.ime.split(" ");
                prikaziGraf(ime, prezime,d.naslov_rada);
            } else {
                const [ime, prezime] = d.ime.split(" ");
                prikaziStatistiku(ime, prezime);
            }
        })
         .on("mouseover", function(event, d) {
         ispisPodataka.style("visibility", "visible")
       .html(`
    <strong>${d.ime}</strong><br>
    ${d.uloga === "student" ? `
        ${d.smer && d.smer !== "None" ? `Смер: ${d.smer}<br>` : ""}
        ${d.tip_teze && d.tip_teze !== "None" ? `Тип тезе: ${d.tip_teze}<br>` : ""}
        ${d.naslov_rada && d.naslov_rada !== "None" ? `Наслов: ${d.naslov_rada}<br>` : ""}
        ${d.godina_odbrane && d.godina_odbrane !== "None" ? `Година одбране: ${d.godina_odbrane}` : ""}
    ` : ""}
    ${d.uloga === "mentor" || d.uloga === "clan_komisije" ? `
        ${d.institucija && d.institucija !== "None" ? `Институција: ${d.institucija}` : ""}
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
        
    cvor.append("text")
        .attr("y", 20)
        .style("text-anchor", "middle")
        .text(d => d.ime)
    simulacija.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        cvor.attr("transform", d => `translate(${d.x},${d.y})`);
    });
    function zapocniPovlacenje(event, d) {
        if (!event.active) simulacija.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    function povlacenje(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    function zavrsiPovlacenje(event, d) {
        if (!event.active) simulacija.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}
