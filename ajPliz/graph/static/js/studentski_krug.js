document.addEventListener("DOMContentLoaded", () => {
    ucitajKrug();
});

function ucitajKrug() {
    const { studenti, profesori, veze } = window.STUDENTSKI_KRUG_PODACI;
    const ispisPodataka = d3.select("#tooltip");

    const sirina = 2500;
    const visina = 2500;
    const spoljasnjiUgao = Math.min(sirina, visina) / 2 - 200;
    const unutrasnjiUgao = spoljasnjiUgao - 500;

    const studentiUnikatni = Array.from(
        new Map(studenti.map(s => [`${s.ime}||${s.naslov_rada}`, s])).values()
    );
    const profesoriUnikatni = Array.from(new Map(profesori.map(p => [p.ime, p])).values());

    const svg = d3.select("#tree")
        .append("svg")
        .attr("width", sirina)
        .attr("height", visina)
        .append("g")
        .attr("transform", `translate(${sirina / 2}, ${visina / 2})`);

    const ugaoStudenata = (2 * Math.PI) / studentiUnikatni.length;
    const ugaoProfesora = (2 * Math.PI) / profesoriUnikatni.length;

    // STUDENTI
    const studentskiCvorovi = svg.selectAll(".student-node")
        .data(studentiUnikatni)
        .enter()
        .append("g")
        .attr("transform", (d, i) => {
            const a = i * ugaoStudenata;
            return `translate(${Math.cos(a) * spoljasnjiUgao}, ${Math.sin(a) * spoljasnjiUgao})`;
        });

    studentskiCvorovi.append("circle")
        .attr("r", 5)
        .attr("fill", "#69b3a2")
        .on("click", (e, d) => {
            const [ime, prezime] = d.ime.split(" ");
            console.log("info bajo:",d.smer)
            prikaziGraf(ime, prezime,d.naslov_rada);
        })
        .on("mouseover", (e, d) => {
            ispisPodataka.style("visibility", "visible")
                .html(`
                    <strong>${d.ime}</strong><br>
                    Смер: ${d.smer}<br>
                    Наслов: ${d.naslov_rada}<br>
                    Година: ${d.godina_odbrane}<br>
                    Тип тезе: ${d.tip_teze}
                `)
                .style("left", e.pageX + 10 + "px")
                .style("top", e.pageY + 10 + "px");
        })
        .on("mouseout", () => ispisPodataka.style("visibility", "hidden"));

    studentskiCvorovi.append("text")
        .attr("dy", -20)
        .text(d => d.ime)
        .style("font-size", "6px");

    // PROFESORI
    const profesorskiCvorovi = svg.selectAll(".professor-node")
        .data(profesoriUnikatni)
        .enter()
        .append("g")
        .attr("transform", (d, i) => {
            const a = i * ugaoProfesora;
            return `translate(${Math.cos(a) * unutrasnjiUgao}, ${Math.sin(a) * unutrasnjiUgao})`;
        })
        .on("click", (e, d) => {
            const [ime, prezime] = d.ime.split(" ");
            prikaziStatistiku(ime, prezime);
        });

    profesorskiCvorovi.append("circle")
        .attr("r", 7)
        .attr("fill", "#f39c12")
        .on("mouseover", (e, d) => {
            ispisPodataka.style("visibility", "visible")
                .html(`<strong>${d.ime}</strong><br>Институција: ${d.institucija}`)
                .style("left", e.pageX + 10 + "px")
                .style("top", e.pageY + 10 + "px");
        })
        .on("mouseout", () => ispisPodataka.style("visibility", "hidden"));

    profesorskiCvorovi.append("text")
        .attr("dy", -20)
        .text(d => d.ime)
        .style("font-size", "6px");

    // VEZE
    const bojaVeze = d3.scaleOrdinal(d3.schemeCategory10);

    svg.selectAll(".link")
        .data(veze)
        .enter()
        .append("line")
        .attr("stroke", (d, i) => bojaVeze(i))
        .attr("stroke-width", 2)
        .attr("x1", d => pozicijaStudenta(d.source, d.naslov_rada).x)
        .attr("y1", d => pozicijaStudenta(d.source, d.naslov_rada).y)
        .attr("x2", d => pozicijaProfesora(d.target).x)
        .attr("y2", d => pozicijaProfesora(d.target).y);

    function pozicijaStudenta(ime, naslov_rada) {
        const i = studentiUnikatni.findIndex(s => s.ime === ime && s.naslov_rada === naslov_rada);
        const a = i * ugaoStudenata;
        return { x: Math.cos(a) * spoljasnjiUgao, y: Math.sin(a) * spoljasnjiUgao };
    }

    function pozicijaProfesora(ime) {
        const i = profesoriUnikatni.findIndex(p => p.ime === ime);
        const a = i * ugaoProfesora;
        return { x: Math.cos(a) * unutrasnjiUgao, y: Math.sin(a) * unutrasnjiUgao };
    }
}
