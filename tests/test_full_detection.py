from __future__ import annotations

from os import pardir, path

import pytest

from charset_normalizer.api import from_bytes, from_path

DIR_PATH = path.join(path.dirname(path.realpath(__file__)), pardir)


@pytest.mark.parametrize(
    "input_data_file, expected_charset, expected_language",
    [
        ("sample-arabic-1.txt", "cp1256", "Arabic"),
        ("sample-french-1.txt", "cp1252", "French"),
        ("sample-arabic.txt", "utf_8", "Arabic"),
        ("sample-russian-3.txt", "utf_8", "Russian"),
        ("sample-french.txt", "utf_8", "French"),
        ("sample-chinese.txt", "big5", "Chinese"),
        ("sample-greek.txt", "cp1253", "Greek"),
        ("sample-greek-2.txt", "cp1253", "Greek"),
        ("sample-hebrew-2.txt", "cp1255", "Hebrew"),
        ("sample-hebrew-3.txt", "cp1255", "Hebrew"),
        ("sample-bulgarian.txt", "utf_8", "Bulgarian"),
        ("sample-english.bom.txt", "utf_8", "English"),
        ("sample-spanish.txt", "utf_8", "Spanish"),
        ("sample-korean.txt", "cp949", "Korean"),
        ("sample-turkish.txt", "cp1254", "Turkish"),
        ("sample-russian-2.txt", "utf_8", "Russian"),
        ("sample-russian.txt", "mac_cyrillic", "Russian"),
        ("sample-polish.txt", "utf_8", "Polish"),
    ],
)
def test_elementary_detection(
    input_data_file: str,
    expected_charset: str,
    expected_language: str,
):
    best_guess = from_path(DIR_PATH + f"/data/{input_data_file}").best()

    assert (
        best_guess is not None
    ), f"Elementary detection has failed upon '{input_data_file}'"
    assert (
        best_guess.encoding == expected_charset
    ), f"Elementary charset detection has failed upon '{input_data_file}'"
    assert (
        best_guess.language == expected_language
    ), f"Elementary language detection has failed upon '{input_data_file}'"


@pytest.mark.parametrize(
    "source_encoding, expected_charset, text",
    [
        (
            "cp1252",
            "cp1252",
            (
                "El ayuntamiento aprobó ayer el presupuesto para el próximo año. "
                "Según el alcalde, la construcción de la nueva biblioteca comenzará en otoño "
                "y estará terminada antes de la Navidad. Muchos vecinos señalaron que el "
                "tráfico en la avenida principal ha aumentado mucho, sobre todo por la mañana."
            ),
        ),
        (
            "cp1252",
            "cp1252",
            (
                "Date;Libellé;Montant\n"
                "01/11/2026;Virement reçu salaire;246,06\n"
                "02/11/2026;Café de la Gare;-165,68\n"
                "03/11/2026;Prélèvement énergie;82,10\n"
                "04/11/2026;Achat boulangerie Noël;14,50\n"
                "05/11/2026;Remboursement hôtel Lyon;95,40\n"
                "06/11/2026;Librairie Théâtre Montparnasse;-32,90\n"
            ),
        ),
        (
            "latin_1",
            "cp1252",
            (
                "Date;Libellé;Montant\n"
                "01/11/2026;Virement reçu salaire;246,06\n"
                "02/11/2026;Café de la Gare;-165,68\n"
                "03/11/2026;Prélèvement énergie;82,10\n"
                "04/11/2026;Achat boulangerie Noël;14,50\n"
            ),
        ),
        (
            "cp1252",
            "cp1252",
            (
                "A construção da nova biblioteca municipal começará no próximo outono "
                "e estará concluída antes do Natal. Muitos moradores afirmaram que a "
                "solução apresentada pela câmara melhorará a circulação na região central."
            ),
        ),
        (
            "cp1252",
            "cp1252",
            (
                "L'amministrazione comunale ha approvato ieri il bilancio per il prossimo anno. "
                "Secondo il sindaco, la costruzione della nuova biblioteca inizierà in autunno "
                "e sarà completata prima di Natale. Perché così tanti cittadini chiedono servizi?"
            ),
        ),
        (
            "cp1250",
            "cp1250",
            (
                "Městská rada včera schválila rozpočet na příští rok. Podle starosty začne "
                "stavba nové knihovny na podzim a bude dokončena před Vánoci."
            ),
        ),
        (
            "cp1250",
            "cp1250",
            (
                "Rada miejska przyjęła wczoraj budżet na przyszły rok. Według burmistrza "
                "budowa nowej biblioteki rozpocznie się jesienią i zostanie ukończona przed świętami."
            ),
        ),
        (
            "cp1250",
            "cp1250",
            (
                "Mestská rada včera schválila rozpočet na budúci rok. Podľa primátora sa "
                "výstavba novej knižnice začne na jeseň a bude dokončená pred Vianocami."
            ),
        ),
        (
            "cp1250",
            "cp1250",
            (
                "A városi tanács tegnap elfogadta a jövő évi költségvetést. A polgármester "
                "szerint az új könyvtár építése ősszel kezdődik és karácsony előtt befejeződik."
            ),
        ),
        (
            "cp1250",
            "cp1250",
            (
                "Gradsko vijeće jučer je odobrilo proračun za sljedeću godinu. Prema riječima "
                "gradonačelnika, izgradnja nove knjižnice počet će u jesen prije Božića."
            ),
        ),
        (
            "cp1254",
            "cp1254",
            (
                "Belediye meclisi dün gelecek yılın bütçesini onayladı. Belediye başkanına göre "
                "yeni kütüphanenin inşaatı sonbaharda başlayacak ve yılbaşından önce tamamlanacak."
            ),
        ),
        (
            "cp1257",
            "cp1257",
            (
                "Miesto taryba vakar patvirtino kitų metų biudžetą. Pasak mero, naujos bibliotekos "
                "statyba prasidės rudenį ir bus baigta iki Kalėdų."
            ),
        ),
        (
            "cp1257",
            "cp1257",
            (
                "Pilsētas dome vakar apstiprināja nākamā gada budžetu. Pēc mēra teiktā, "
                "jaunās bibliotēkas būvniecība sāksies rudenī un tiks pabeigta līdz Ziemassvētkiem. "
                "Daudzi iedzīvotāji norādīja uz satiksmes pieaugumu."
            ),
        ),
    ],
)
def test_european_single_byte_latin_orthography(
    source_encoding: str, expected_charset: str, text: str
):
    best_guess = from_bytes(text.encode(source_encoding)).best()

    assert best_guess is not None
    assert best_guess.encoding == expected_charset
    assert str(best_guess) == text


@pytest.mark.parametrize(
    "source_encoding, expected_charset, text",
    [
        ("cp1252", "cp1252", "El próximo año"),
        ("cp1252", "cp1252", "Café crème"),
        ("cp1254", "cp1254", "İstanbul güneşli"),
    ],
)
def test_short_latin_orthography_and_turkish_dotted_i(
    source_encoding: str, expected_charset: str, text: str
):
    best_guess = from_bytes(text.encode(source_encoding)).best()

    assert best_guess is not None
    assert best_guess.encoding == expected_charset
    assert str(best_guess) == text
