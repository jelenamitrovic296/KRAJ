// utils.js — zajedničke pomoćne funkcije

function prikaziPoruku(porukaGreske, poruka) {
    porukaGreske.textContent = poruka;
    porukaGreske.style.display = "block";
    porukaGreske.scrollIntoView({ behavior: "smooth" });
    alert(poruka);
    event.preventDefault();
}

function validirajGodinu(godina) {
    return /^\d+$/.test(godina) && parseInt(godina) >= 2000;
}

function obrisiNepotrebneParametre(url, parametriZaBrisanje) {
    parametriZaBrisanje.forEach(param => url.searchParams.delete(param));
}
