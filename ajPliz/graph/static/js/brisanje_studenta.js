
document.addEventListener("DOMContentLoaded", () => {
    const tabela = document.getElementById("tabela-studenata-za-brisanje");
    if (!tabela) return;

    tabela.addEventListener("click", (event) => {
        const dugme = event.target.closest(".btn-izbrisi-studenta");
        if (!dugme) return;

        const red = dugme.closest("tr");
        const ime = red.dataset.ime;
        const prezime = red.dataset.prezime;
        const naslov = red.dataset.naslov;

        const potvrda = confirm(
            `Да ли сигурно желите да обришете студента ${ime} ${prezime} (наслов рада: "${naslov}") из базе? Ова акција је неповратна.`
        );
        if (!potvrda) return;

        document.getElementById("hidden_ime_studenta_za_brisanje").value = ime;
        document.getElementById("hidden_prezime_studenta_za_brisanje").value = prezime;
        document.getElementById("hidden_naslov_rada_studenta_za_brisanje").value = naslov;

        document.getElementById("forma-za-stvarno-brisanje-studenta").submit();
    });
});
