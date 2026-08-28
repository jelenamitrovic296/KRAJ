document.addEventListener("DOMContentLoaded", () => {
    const tabela = document.getElementById("tabela-studenata");
    if (!tabela) return;

    tabela.addEventListener("click", (event) => {
        const dugme = event.target.closest(".btn-prikazi-graf");
        if (!dugme) return;

        const red = dugme.closest("tr");
        const ime = red.dataset.ime;
        const prezime = red.dataset.prezime;
        const naslov = red.dataset.naslov;


        if (ime && prezime && naslov) {
             prikaziGraf(ime, prezime,naslov)
        }
    });
});
