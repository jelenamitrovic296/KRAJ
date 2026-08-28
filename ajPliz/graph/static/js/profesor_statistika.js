// static/js/profesor_statistika.js

function prikaziStatistikuProfesora(podaci) {
    const statistikaContainer = document.getElementById('statistika-container');
    const profesoriContainer = document.getElementById('profesori-institucija-container');

    if (!podaci) {
        console.error("Nema podataka za prikaz statistike");
        return;
    }

    // ================= STATISTIKA TABELA =================
    if (podaci.statistika && podaci.statistika.length > 0) {
        let statistikaHTML = `
            <h2 class="table-title">Статистика за професора ${podaci.ime_profesora} ${podaci.prezime_profesora}</h2>
            <div class="table-container">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Тип</th>
                            <th>Број студената</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        podaci.statistika.forEach(red => {
            statistikaHTML += `
                <tr>
                    <td>${red.tip}</td>
                    <td>${red.broj_studenta}</td>
                </tr>
            `;
        });

        statistikaHTML += `
                    </tbody>
                </table>
            </div>
        `;

        statistikaContainer.innerHTML = statistikaHTML;
    }

    // ================= PROFESORI SA INSTITUCIJE =================
    if (podaci.profesori_sa_izabrane_institucije && podaci.profesori_sa_izabrane_institucije.length > 0) {
        let profesoriHTML = `
            <h2 class="table-title">Професори са изабране институције</h2>
            <div class="table-container">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Име</th>
                            <th>Презиме</th>
                            <th>Институција</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        podaci.profesori_sa_izabrane_institucije.forEach(profesor => {
            profesoriHTML += `
                <tr>
                    <td>${profesor[0]}</td>
                    <td>${profesor[1]}</td>
                    <td>${profesor[2]}</td>
                </tr>
            `;
        });

        profesoriHTML += `
                    </tbody>
                </table>
            </div>
        `;

        profesoriContainer.innerHTML = profesoriHTML;
    }
}

// ================= INIT =================
document.addEventListener("DOMContentLoaded", () => {
    if (typeof podaciStatistikaProfesora !== "undefined") {
        prikaziStatistikuProfesora(podaciStatistikaProfesora);
    }
});
