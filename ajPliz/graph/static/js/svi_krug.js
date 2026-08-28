document.addEventListener("DOMContentLoaded", () => {
    ucitajGraf();
});

function ucitajGraf() {
    const { studenti, profesori, kolege } = window.SVI_PODACI;
    const ispisPodataka = d3.select("#tooltip");

    const sirina = 7000;
    const visina = 7000;
    const spoljasnjiUgao = Math.min(sirina, visina) / 2 - 200;
    const unutrasnjiUgao = spoljasnjiUgao - 100;

    const svg = d3.select("#tree")
        .append("svg")
        .attr("width", sirina)
        .attr("height", visina)
        .append("g")
        .attr("transform", `translate(${sirina / 2}, ${visina / 2})`);

    const ugaoStudenata = (2 * Math.PI) / studenti.length;
    const ugaoProfesora = (2 * Math.PI) / profesori.length;

    // STUDENTI
    const studentskiCvorovi = svg.selectAll(".student-node")
        .data(studenti)
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
        .text(d => d.ime.split(" ").map(x => x[0]).join("."))
        .style("font-size", "6px");

    // PROFESORI
    const profesorskiCvorovi = svg.selectAll(".professor-node")
        .data(profesori)
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

    // VEZE KOLEGE–KOLEGE (BEZ DUPLIKATA)
    const postojeceVeze = new Set();
    const komisijaVeze = [];

    kolege.forEach(v => {
        const k1 = v.od + "->" + v.ka;
        const k2 = v.ka + "->" + v.od;
        if (!postojeceVeze.has(k1) && !postojeceVeze.has(k2)) {
            komisijaVeze.push(v);
            postojeceVeze.add(k1);
            postojeceVeze.add(k2);
        }
    });

    const bojaVeze = d3.scaleOrdinal(d3.schemeCategory10);

    svg.selectAll(".komisija-link")
        .data(komisijaVeze)
        .enter()
        .append("line")
        .attr("stroke", (d, i) => bojaVeze(i))
        .attr("stroke-width", 2)
        .attr("x1", d => pozicijaProfesora(d.od).x)
        .attr("y1", d => pozicijaProfesora(d.od).y)
        .attr("x2", d => pozicijaProfesora(d.ka).x)
        .attr("y2", d => pozicijaProfesora(d.ka).y);

    function pozicijaProfesora(ime) {
        const i = profesori.findIndex(p => p.ime === ime);
        const a = i * ugaoProfesora;
        return {
            x: Math.cos(a) * unutrasnjiUgao,
            y: Math.sin(a) * unutrasnjiUgao
        };
    }
}
