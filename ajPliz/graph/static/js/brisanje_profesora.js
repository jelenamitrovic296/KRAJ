// brisanje_profesora.js — klik na "Избриши" u tabeli rezultata pretrage za brisanje profesora

document.addEventListener("DOMContentLoaded", () => {
    const tabela = document.getElementById("tabela-profesora-za-brisanje");
    if (!tabela) return;

    tabela.addEventListener("click", (event) => {
        const dugme = event.target.closest(".btn-izbrisi-profesora");
        if (!dugme) return;

        const red = dugme.closest("tr");
        const ime = red.dataset.ime;
        const prezime = red.dataset.prezime;
        const institucija = red.dataset.institucija;

        const potvrda = confirm(
            `Да ли сигурно желите да обришете професора ${ime} ${prezime} (${institucija}) из базе? Ова акција је неповратна.`
        );
        if (!potvrda) return;

        document.getElementById("hidden_ime_profesora_za_brisanje").value = ime;
        document.getElementById("hidden_prezime_profesora_za_brisanje").value = prezime;
        document.getElementById("hidden_institucija_profesora_za_brisanje").value = institucija;

        document.getElementById("forma-za-stvarno-brisanje-profesora").submit();
    });
});
