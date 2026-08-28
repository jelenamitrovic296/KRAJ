// validacije.js — sve validacione funkcije za forme

function proveriUnosInstitucije(event) {
    const institucija = document.getElementById('naziv_institucije').value.trim();
    const porukaGreske = document.getElementById('poruka-za-pretragu-profesora');

    if (!institucija) {
        prikaziPoruku(porukaGreske, "Молимо вас да унесете институцију по којој желите да претражите професоре.");
    }
}

function proveriUnosImenaIPrezimenaProfesora(event) {
    const ime = document.getElementById('ime_profesora').value.trim();
    const prezime = document.getElementById('prezime_profesora').value.trim();
    const porukaGreske = document.getElementById('poruka-za-pretragu-profesora');

    if (!ime || !prezime) {
        prikaziPoruku(porukaGreske, "Морате унети име и презиме професора.");
    }
}

function proveriUnosZaJednogStudenta(nazivPoljaIme, nazivPoljaPrezime,nazivPoljaNaslov,event) {
    const ime = document.getElementById("ime_studenta").value.trim();
    const prezime = document.getElementById("prezime_studenta").value.trim();
    const naslov = document.getElementById("naslov_jednog").value.trim();
    

    const porukaGreske = document.getElementById("poruka-greske");

    // Provera da li su sva polja uneta
    if (!ime || !prezime || !naslov) {
        const poruka = "Да би се извршила претрага једног студента, потребно је унети све податке. Уколико нисте сигурни у неке информације, можете користити форму за претрагу више студената.";
        prikaziPoruku(porukaGreske, poruka);
        return false;
    }



    porukaGreske.style.display = "none";

    //prikaziGraf(ime, prezime,smer,naslov,tipTeze,godina);
}

function proveriUnosNovogProfesora(imeNovogProfesora, prezimeNovogProfesora, institucijaProfesora, event) {
    const ime = document.getElementById(imeNovogProfesora).value.trim();
    const prezime = document.getElementById(prezimeNovogProfesora).value.trim();
    const institucija = document.getElementById(institucijaProfesora).value.trim();
    const porukaGreske = document.getElementById("poruka-za-dodavanje-profesora");

    if (!ime || !prezime || !institucija) {
        prikaziPoruku(porukaGreske, "Молимо вас да унесете име и презиме професора, као и институцију у којој је запослен, да бисте га додали у базу података.");
    }
}
function proveriDodavanjeIAzuriranjeInformacija(
    ime_s, prezime_s, smer_s, tip_teze_s, naslov_s,
    godina_odbrane_s, mentor_id_s, komisija_container_s, naslov_rada_studenta_za_azuriranje = null, event
) {
    const ime            = document.getElementById(ime_s).value.trim();
    const prezime        = document.getElementById(prezime_s).value.trim();
    const smer           = document.getElementById(smer_s).value.trim();
    const tip_teze       = document.getElementById(tip_teze_s).value.trim();
    const naslov         = document.getElementById(naslov_s).value.trim();
    const godina_odbrane = document.getElementById(godina_odbrane_s).value.trim();
    const mentor_id      = document.getElementById(mentor_id_s).value.trim();

    const naslovRadaEl = naslov_rada_studenta_za_azuriranje
        ? document.getElementById(naslov_rada_studenta_za_azuriranje)
        : null;
    const naslov_rada = naslovRadaEl ? naslovRadaEl.value.trim() : "";

    const komisijaSelects = document.querySelectorAll(`#${komisija_container_s} select`);
    const imaClana = Array.from(komisijaSelects).some(s => s.value.trim() !== '');

    const porukaGreske = (ime_s === "ime_novog_studenta")
        ? document.getElementById('poruka-greske-za-dodavanje')
        : document.getElementById('poruka-greske-za-azuriranje');

    const jeAzuriranje = ime_s !== "ime_novog_studenta";

    const provere = [
       { uslov: jeAzuriranje && (!ime || !prezime || !naslov_rada), poruka: "Име, презиме и наслов рада студента морају бити унети ради идентификације." },
       { uslov: !jeAzuriranje && (!ime || !prezime), poruka: "Морате унети име и презиме студента." },
       { uslov: !smer,                            poruka: "Морате унети смер студента." },
       { uslov: !tip_teze,                        poruka: "Морате унети тип тезе." },
       { uslov: !naslov,                          poruka: "Морате унети наслов рада." },
       { uslov: !godina_odbrane,                  poruka: "Мора бити унесена година одбране." },
       { uslov: !validirajGodinu(godina_odbrane), poruka: "Година одбране није исправна!" },
       { uslov: !mentor_id,                       poruka: "Морате изабрати ментора." },
       { uslov: !imaClana,                        poruka: "Морате изабрати бар једног члана комисије." },
        
    ];

    for (const { uslov, poruka } of provere) {
        if (uslov) {
            prikaziPoruku(porukaGreske, poruka);
            event.preventDefault();
            return;
        }
    }

    porukaGreske.style.display = "none";
}
function proveriFormuZaBrisanje(nazivPoljaIme, nazivPoljaPrezime, nazivPoljaNaslovInstitucija, event) {
    const ime      = document.getElementById(nazivPoljaIme).value.trim();
    const prezime  = document.getElementById(nazivPoljaPrezime).value.trim();
    const trece    = document.getElementById(nazivPoljaNaslovInstitucija).value.trim();
    const jeProfesar = nazivPoljaIme === 'ime_profesora_za_brisanje';
    const porukaGreske = jeProfesar
        ? document.getElementById("poruka-za-brisanje-profesor")
        : document.getElementById('poruka-za-brisanje-student');

    if (!ime || !prezime || !trece) {
        const poruka = jeProfesar
            ? "Морате унети име, презиме и назив институције професора којег желите да обришете из базе података."
            : "Морате унети име, презиме и наслов рада студента којег желите да обришете из базе података.";
        prikaziPoruku(porukaGreske, poruka);
        event.preventDefault();
    }
}

function proveriFormuZaPretraguBrisanjaStudenta(nazivPoljaIme, nazivPoljaPrezime, event) {
    const ime      = document.getElementById(nazivPoljaIme).value.trim();
    const prezime  = document.getElementById(nazivPoljaPrezime).value.trim();
    const porukaGreske = document.getElementById('poruka-za-brisanje-student');

    if (!ime || !prezime) {
        prikaziPoruku(porukaGreske, "Морате унети име и презиме студента којег желите да претражите ради брисања.");
        event.preventDefault();
    }
}

function proveriFormuZaPretraguAzuriranjaStudenta(nazivPoljaIme, nazivPoljaPrezime, event) {
    const ime      = document.getElementById(nazivPoljaIme).value.trim();
    const prezime  = document.getElementById(nazivPoljaPrezime).value.trim();
    const porukaGreske = document.getElementById('poruka-za-azuriranje-pretraga-student');

    if (!ime || !prezime) {
        prikaziPoruku(porukaGreske, "Морате унети име и презиме студента којег желите да претражите ради ажурирања.");
        event.preventDefault();
    }
}

function proveriFormuZaPretraguBrisanjaProfesora(nazivPoljaIme, nazivPoljaPrezime, event) {
    const ime      = document.getElementById(nazivPoljaIme).value.trim();
    const prezime  = document.getElementById(nazivPoljaPrezime).value.trim();
    const porukaGreske = document.getElementById('poruka-za-brisanje-profesor');

    if (!ime || !prezime) {
        prikaziPoruku(porukaGreske, "Морате унети име и презиме професора којег желите да претражите ради брисања.");
        event.preventDefault();
    }
}

function proveriUnosZaViseStudenata(
    nazivPoljaIme, nazivPoljaPrezime, nazivPoljaSmer,
    nazivPoljaNaslov, nazivPoljaGodinaOdbrane,
    nazivPoljaGodinaOd, nazivPoljaGodinaDo,
    nazivPoljaTipTeze, event
) {
    const ime           = document.getElementById(nazivPoljaIme).value.trim();
    const prezime       = document.getElementById(nazivPoljaPrezime).value.trim();
    const smer          = document.getElementById(nazivPoljaSmer).value.trim();
    const naslov        = document.getElementById(nazivPoljaNaslov).value.trim();
    const godinaOdbrane = document.getElementById(nazivPoljaGodinaOdbrane).value.trim();
    const godinaOd      = document.getElementById(nazivPoljaGodinaOd).value.trim();
    const godinaDo      = document.getElementById(nazivPoljaGodinaDo).value.trim();
    const tipTeze       = document.getElementById(nazivPoljaTipTeze).value.trim();
    const prikazOpcije  = document.querySelectorAll('input[name="prikaz"]:checked');
    const porukaGreske  = document.getElementById("poruka-greske-vise-studenata");

    if (prikazOpcije.length === 0) {
        prikaziPoruku(porukaGreske, "Морате изабрати један начин приказа.");
        return;
    }

    if (!ime && !prezime && !smer && !naslov && !godinaOdbrane && !godinaOd && !godinaDo && !tipTeze) {
        prikaziPoruku(porukaGreske, "Морате унети бар један параметар за претрагу.");
        return;
    }

    if (godinaOdbrane) {
        if (!validirajGodinu(godinaOdbrane)) {
            prikaziPoruku(porukaGreske, "Година одбране мора бити број већи или једнак 2000.");
            return;
        }
        if (godinaOd || godinaDo) {
            prikaziPoruku(porukaGreske, "Ако је унесена година одбране, не можете уносити годину од или годину до.");
            return;
        }
    } else {
        if (godinaOd && !validirajGodinu(godinaOd)) {
            prikaziPoruku(porukaGreske, "Година од мора бити број већи или једнак 2000.");
            return;
        }
        if (godinaDo && !validirajGodinu(godinaDo)) {
            prikaziPoruku(porukaGreske, "Година до мора бити број већи или једнак 2000.");
            return;
        }
        if (godinaOd && godinaDo && parseInt(godinaOd) > parseInt(godinaDo)) {
            prikaziPoruku(porukaGreske, "Година од не може бити већа од године до.");
            return;
        }
    }

    porukaGreske.style.display = "none";
}
