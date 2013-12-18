# encoding: utf-8

revision = '2f0625b248bc'
down_revision = '236f754feafc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    op.add_column('lu_threats',
        sa.Column('name_ro', sa.UnicodeText, nullable=True))

    lu_threats_codes = table('lu_threats',
        column('code', sa.String),
        column('name_ro', sa.UnicodeText))

    for code, name_ro in DATA:
        op.execute(
            lu_threats_codes.update()
                .where(lu_threats_codes.c.code == op.inline_literal(code))
                .values({'name_ro': op.inline_literal(name_ro)}))


def downgrade():
    op.drop_column('lu_threats', 'name_ro')


DATA = [
    ("A", u"Agricultura"),
    ("A01", u"Cultivare"),
    ("A02", u"Modificarea practicilor de cultivare"),
    ("A02.01", u"Agricultura intensiva"),
    ("A02.02", u"Schimbarea culturii"),
    ("A02.03", u"Inlocuirea pasunii cu terenuri arabile"),
    ("A03", u"Cosire/Taiere a pasunii"),
    ("A03.01", u"Cosire intensiva sau intensificarea cosirii"),
    ("A03.02", u"Cosire ne-intensiva"),
    ("A03.03", u"Abandonarea/lipsa cosirii"),
    ("A04", u"Pasunatul"),
    ("A04.01", u"Pasunatul intensiv"),
    ("A04.01.01", u"Pasunatul intensiv al vacilor"),
    ("A04.01.02", u"Pasunatul intensiv al oilor"),
    ("A04.01.03", u"Pasunatul intensiv al cailor"),
    ("A04.01.04", u"Pasunatul intensiv al caprelor"),
    ("A04.01.05", u"Pasunatul intensiv in amestec de animale"),
    ("A04.02", u"Pasunatul neintensiv"),
    ("A04.02.01", u"Pasunatul ne-intensiv al vacilor"),
    ("A04.02.02", u"Pasunatul ne-intensiv al oilor"),
    ("A04.02.03", u"Pasunatul ne-intensiv al cailor"),
    ("A04.02.04", u"Pasunatul ne-intensiv al caprelor"),
    ("A04.02.05", u"Pasunatul ne-intensiv in amestec de animale"),
    ("A04.03", u"Abandonarea sistemelor pastorale, lipsa pasunatului"),
    ("A05", u"Cresterea animalelor (fara pasunat)"),
    ("A05.01", u"Cresterea animalelor"),
    ("A05.02", u"Furajare"),
    ("A05.03", u"Lipsa cresterii animalelor"),
    ("A06", u"Culturi anuale si perene nelemnoase"),
    ("A06.01", u"Culturi anuale pentru productia de alimente"),
    ("A06.01.01", u"Culturi anuale intensive pentru productia de alimente/(intensificarea culturilor anuale pentru productia de alimente"),
    ("A06.01.02", u"Culturi anuale ne-intensive pentru productia de alimente"),
    ("A06.02", u"Culturi perene nelemnoase"),
    ("A06.02.01", u"Culturi perene nelemnoase intensive/intensificarea culturilor (perene nelemnoase"),
    ("A06.02.02", u"Culturi perene nelemnoase neintensive"),
    ("A06.03", u"Productie de biocombustibili"),
    ("A06.04", u"Abandonarea culturii pentru productie"),
    ("A07", u"Utilizarea produselor biocide, hormoni si substante chimice"),
    ("A08", u"Fertilizarea (cu ingrasamant)"),
    ("A09", u"Irigarea"),
    ("A10", u"Restructurarea detinerii terenului agricol"),
    ("A10.01", u"Indepartarea gardurilor vii si a crangurilor sau tufisurilor"),
    ("A10.02", u"Indepartarea zidurilor din piatra si a digurilor"),
    ("A11", u"Alte activitati agricole decat cele listate mai sus"),
    ("B", u"Silvicultura"),
    ("B01", u"Plantarea de padure pe teren deschis"),
    ("B01.01", u"Plantare padure, pe teren deschis (copaci nativi)"),
    ("B01.02", u"Plantare artificiala, pe teren deschis (copaci nenativi)"),
    ("B02", u"Gestionarea si utilizarea padurii si plantatiei"),
    ("B02.01", u"Replantarea padurii"),
    ("B02.01.01", u"Replantarea padurii (copaci nativi)"),
    ("B02.01.02", u"Replantarea padurii (copaci nenativi)"),
    ("B02.02", u"Curatarea padurii"),
    ("B02.03", u"Indepartarea lastarisului"),
    ("B02.04", u"Indepartarea arborilor uscati sau in curs de uscare"),
    ("B02.05", u"Productia lemnoasa ne-intensiva (lasarea lemnului mort/neatingerea (de copacii vechi)"),
    ("B02.06", u"Decojirea scoartei copacului"),
    ("B03", u"Exploatare forestiera fara replantare sau refacere naturala"),
    ("B04", u"Folosirea biocidelor, hormonilor si chimicalelor (in padure)"),
    ("B05", u"Folosirea de ingrasaminte (in padure)"),
    ("B06", u"Pasunatul in padure/in zona impadurita"),
    ("B07", u"Alte activitati silvice decat cele listate mai sus"),
    ("C", u"Minerit, extractia de materiale si de productie de energie"),
    ("C01", u"Industria extractiva"),
    ("C01.01", u"Extragere de nisip si pietris"),
    ("C01.01.01", u"Cariere de nisip si pietris"),
    ("C01.01.02", u"Scoaterea de material de pe plaje"),
    ("C01.02", u"Puturi de argila (lut) si chirpici"),
    ("C01.03", u"Extractia de turba"),
    ("C01.03.01", u"Extragerea manuala a turbei"),
    ("C01.03.02", u"Extragerea mecanizat a turbei"),
    ("C01.04", u"Mine"),
    ("C01.04.01", u"Minerit de suprafata"),
    ("C01.04.02", u"Minerit subteran"),
    ("C01.05", u"Saline"),
    ("C01.05.01", u"Saline abandonate"),
    ("C01.05.02", u"Saline modificate"),
    ("C01.06", u"Prospectiuni geotehnice"),
    ("C01.07", u"Minerit si activitati de extragere la care nu se refera mai sus"),
    ("C02", u"Exploatarea si extractia de petrol si gaze"),
    ("C02.01", u"Foraj de explorare"),
    ("C02.02", u"Foraj de productie"),
    ("C02.03", u"Instalatii de foraj"),
    ("C02.04", u"Instalatii semi-submersibile"),
    ("C02.05", u"Foraj cu ajutorul navelor speciale pentru foraj"),
    ("C03", u"Utilizarea energiei din surse regenerabile abiotice"),
    ("C03.01", u"Geotermala"),
    ("C03.02", u"Solara"),
    ("C03.03", u"Eoliana"),
    ("C03.04", u"Maree"),
    ("D", u"Retele de comunicatii"),
    ("D01", u"Drumuri, poteci si cai ferate"),
    ("D01.01", u"Poteci,trasee,trasee pentru ciclism"),
    ("D01.02", u"Drumuri, autostrazi"),
    ("D01.03", u"Parcuri auto si parcari"),
    ("D01.04", u"Cai ferate, cai ferate de mare viteza"),
    ("D01.05", u"Poduri, viaducte"),
    ("D01.06", u"Tunele"),
    ("D02", u"Linii de utilitati si servicii"),
    ("D02.01", u"Linii electrice si de telefonie"),
    ("D02.01.01", u"Linii electrice si de telefon suspendate"),
    ("D02.01.02", u"Linii electrice si de telefon subterane/scufundate"),
    ("D02.02", u"Conducte"),
    ("D02.03", u"Piloni si antene de comunicare"),
    ("D02.09", u"Alte forme de transport de energie"),
    ("D03", u"Rute navale, porturi, constructii marine"),
    ("D03.01", u"Zona portuara"),
    ("D03.01.01", u"Rampe"),
    ("D03.01.02", u"Diguri/zone turistice si de agrement"),
    ("D03.01.03", u"Zona de pescuit"),
    ("D03.01.04", u"Zona industrial portuara"),
    ("D03.02", u"Navigatie"),
    ("D03.02.01", u"Benzi de marfa"),
    ("D03.02.02", u"Benzi de transport de pasageri (de mare viteza)"),
    ("D03.03", u"Constructii marine"),
    ("D04", u"Aeroporturi, rute de zbor"),
    ("D04.01", u"Aeroport"),
    ("D04.02", u"Aerodrom, helioport"),
    ("D04.03", u"Rute de zbor"),
    ("D05", u"Imbunatatirea accesului in zona"),
    ("D06", u"Alte forme de transport si comunicatie"),
    ("E", u"Urbanizare, dezvoltare rezidentiala si comerciala"),
    ("E01", u"Zone urbanizate, habitare umana (locuinte umane)"),
    ("E01.01", u"Urbanizare continua"),
    ("E01.02", u"Urbanizare discontinua"),
    ("E01.03", u"Habitare dispersata (locuinte risipite, disperse)"),
    ("E01.04", u"Alte modele(tipuri) de habitare/locuinte"),
    ("E02", u"Zone industriale sau comerciale"),
    ("E02.01", u"Fabrici"),
    ("E02.02", u"Depozite industriale"),
    ("E02.03", u"Alte zone industriale/comerciale"),
    ("E03", u"Descarcari"),
    ("E03.01", u"Depozitarea deseurilor menajere /deseuri provenite din baze de (agrement"),
    ("E03.02", u"Depozitarea deseurilor industriale"),
    ("E03.03", u"Depozitarea materialelor inerte(nereactive)"),
    ("E03.04", u"Alte tipuri de depozitari"),
    ("E03.04.01", u"Depuneri costiere de nisip/cresterea plajelor"),
    ("E04", u"Infrastructuri, constructii in peisaj"),
    ("E04.01", u"Infrastructuri agricole, constructii in peisaj"),
    ("E04.02", u"Baze si constructii militare in peisaj"),
    ("E05", u"Depozite de materiale"),
    ("E06", u"Alte activitati de urbanizare si industriale similare"),
    ("E06.01", u"Demolarea de cladiri si structuri umane"),
    ("E06.02", u"Reconstructia, renovarea cladirilor"),
    ("F", u"Folosirea resurselor biologice, altele decat agricultura si (silvicultura"),
    ("F01", u"Acvacultura marina si de apa dulce"),
    ("F01.01", u"Piscicultura intensiva, intensificata"),
    ("F01.02", u"Culturi suspendate"),
    ("F01.03", u"Culturi bentonice"),
    ("F02", u"Pescuit si recoltarea resurselor acvatice"),
    ("F02.01", u"Pescuit profesional pasiv"),
    ("F02.01.01", u"Cu capcane, varse, vintire etc."),
    ("F02.01.02", u"Cu plasa"),
    ("F02.01.03", u"Cu paragate, in zona litorala"),
    ("F02.01.04", u"Cu paragate, in zona pelagica"),
    ("F02.02", u"Pescuit profesional activ"),
    ("F02.02.01", u"Traule in zona bentonica sau litorala"),
    ("F02.02.02", u"Traule in zona pelagica"),
    ("F02.02.03", u"Pescuit de adancime intr-o locatie fixa (pescuit cu setca / (ava, in zona litorala)"),
    ("F02.02.04", u"Pescuit pelagic intr-o locatie fixa (pescuit cu setca/plasa-(punga, in zona pelagica)"),
    ("F02.02.05", u"Dragare bentonica"),
    ("F02.03", u"Pescuit de agrement"),
    ("F02.03.01", u"Sapat dupa momeala / colectare"),
    ("F02.03.02", u"Pescuit cu undita"),
    ("F02.03.03", u"Pescuit cu ostia"),
    ("F03", u"Vanatoarea si colectarea animalelor salbatice (terestre)"),
    ("F03.01", u"Vanatoare"),
    ("F03.01.01", u"Prejudicii cauzate prin vanatoare (densitatea populationala in (exces)"),
    ("F03.02", u"Luare / prelevare de fauna(terestra)"),
    ("F03.02.01", u"Colectare de animale (insecte, reptile, amfibieni...)"),
    ("F03.02.02", u"Luare din cuib (Falconidaei)"),
    ("F03.02.03", u"Capcane, otravire, braconaj"),
    ("F03.02.04", u"Controlul pradatorilor"),
    ("F03.02.05", u"Captura accidentala"),
    ("F03.02.09", u"Alte forme de luare(extragere) fauna"),
    ("F04", u"Luare/prelevare de plante terestre, in general"),
    ("F04.01", u"Pradarea statiunilor floristice(rezervatiiile floristice)"),
    ("F04.02", u"Colectarea (ciuperci, licheni, fructe de padure etc)"),
    ("F04.02.01", u"Adunare manuala"),
    ("F04.02.02", u"Colectare manuala"),
    ("F05", u"Luare ilegala/prelevare de fauna marina"),
    ("F05.01", u"Dinamita"),
    ("F05.02", u"Pescuit de scoici Lithophaga (nu traiesc in Marea Neagra!!)"),
    ("F05.03", u"Pescuit prin otravire"),
    ("F05.04", u"Braconaj"),
    ("F05.05", u"Vanatoare cu arma"),
    ("F05.06", u"Luarea in scop de colectionare"),
    ("F05.07", u"Altele (ex. cu plase derivante)"),
    ("F06", u"Alte activitati de vanatoare, pescuit sau colectare decat cele de mai (sus"),
    ("F06.01", u"Statii de crestere a pasarilor/vanatului(in general)"),
    ("G", u"Intruziuni si dezechilibre umane"),
    ("G01", u"Sport in aer liber si activitati de petrecere a timpului liber, (activitati recreative"),
    ("G01.01", u"Sporturi nautice"),
    ("G01.01.01", u"Sporturi nautice motorizate"),
    ("G01.01.02", u"Sporturi nautice non-motorizate"),
    ("G01.02", u"Mersul pe jos,calarie si vehicule non-motorizate"),
    ("G01.03", u"Vehicule cu motor"),
    ("G01.03.01", u"Conducerea obisnuita a vehiculelor motorizate"),
    ("G01.03.02", u"Conducerea in afara drumului a vehiculelor motorizate"),
    ("G01.04", u"Drumetii montane, alpinism, speologie."),
    ("G01.04.01", u"Alpinism"),
    ("G01.04.02", u"Speologie"),
    ("G01.04.03", u"Vizite de agrement in pesteri"),
    ("G01.05", u"Planorism, delta plan, parapanta, balon."),
    ("G01.06", u"Ski in afara partiilor"),
    ("G01.07", u"Scubadiving, snorkeling (scufundari cu scafandru autonom sau cu (snorkel)"),
    ("G01.08", u"Alte activitati sportive si recreative in aer liber"),
    ("G02", u"Complexe sportive si de odihna"),
    ("G02.01", u"Terenuri de golf"),
    ("G02.02", u"Complex de ski"),
    ("G02.03", u"Stadion"),
    ("G02.04", u"Circuite auto"),
    ("G02.05", u"Hipodrom"),
    ("G02.06", u"Parc de distractii"),
    ("G02.07", u"Baze sportive"),
    ("G02.08", u"Locuri de campare si zone de parcare pentru rulote"),
    ("G02.09", u"Observatoare ale faunei salbatice"),
    ("G02.10", u"Alte sporturi/complexe de agrement"),
    ("G03", u"Centre de practicare activitati demonstrative"),
    ("G04", u"Utilitati militare si antrenament civil (miscari civile)"),
    ("G04.01", u"Manevre militare"),
    ("G04.02", u"Utilitati militare abandonate"),
    ("G05", u"Alte intruziuni si dezechilibre umane"),
    ("G05.01", u"Tasarea, supraexploatarea"),
    ("G05.02", u"Abraziune de suprafata/deteriorare mecanica a suprafetei fundului (de mare"),
    ("G05.03", u"Penetrare/deteriorarea suprafetei fundului marii"),
    ("G05.04", u"Vandalism"),
    ("G05.05", u"Intretinerea intensiva a parcurilor publice/curatarea plajelor"),
    ("G05.06", u"Curatarea copacilor, taierea pentru siguranta publica, (indepartarea de copaci pe marginea drummului"),
    ("G05.07", u"Lipsa sau indepartarea gresita a masurilor de conservare"),
    ("G05.08", u"Inchiderea pesterilor sau a galeriilor"),
    ("G05.09", u"Garduri, ingradiri"),
    ("G05.10", u"Survolarea cu aeronave(agricol)"),
    ("G05.11", u"Moartea sau ranirea prin colilziune"),
    ("H", u"Poluarea"),
    ("H01", u"Poluarea apelor de suprafata (limnice, terestre, marine si salmastre)"),
    ("H01.01", u"Poluarea apelor de suprafata de catre combinate industriale"),
    ("H01.02", u"Poluarea apelor de suprafata prin inundatii"),
    ("H01.03", u"Alte surse de poluare a apelor de suprafata"),
    ("H01.04", u"Poluarea difuza a apelor de suprafata prin inundatii sau scurgeri (urbane"),
    ("H01.05", u"Poluarea difuza a apelor de suprafata, cauzata de activitati (agricole si forestiere"),
    ("H01.06", u"Poluarea difuza a apelor de suprafata cauzata de transport si de (infrastructura fara conectare la canalizare/masini de maturat strazi"),
    ("H01.07", u"Poluarea difuza a apelor de suprafata cauzata de platformele (industriale abandonate"),
    ("H01.08", u"Poluarea difuza a apelor de suprafata cauzata de apa de canalizare (menajera si de ape uzate"),
    ("H01.09", u"Poluarea difuza a apelor de suprafata cauzata de apa de alte surse (care nu sunt enumerate"),
    ("H02", u"Poluarea apelor subterane (surse punctiforme si difuze)"),
    ("H02.01", u"Poluarii apelor subterane cu scurgeri din zone contaminate"),
    ("H02.02", u"Poluarii apelor subterane cu scurgeri provenite din zone in care (sunt depozitate deseuri"),
    ("H02.03", u"Poluarea apelor subterane asociata cu infrastructura din industria (de petrol"),
    ("H02.04", u"Poluarea apelor subterane prin evacuarea apelor de mina"),
    ("H02.05", u"Popluarea apelor subterane cauzata de descarcarea apei contaminate (de infiltratie"),
    ("H02.06", u"Poluarea difuza a apelor subterane cauzata de activitati agricole (si forestiere"),
    ("H02.07", u"Poluarea difuza a apelor subterane cauzata de non-canalizare"),
    ("H02.08", u"Poluarea difuza a apelor subterane cauzata de terenurile urbane"),
    ("H03", u"Poluarea apei marine"),
    ("H03.01", u"Deversarilor de petrol in mare"),
    ("H03.02", u"Descarcarea de materiale toxice chimice in mare"),
    ("H03.02.01", u"Contaminare cu compusi non-sintetici"),
    ("H03.02.02", u"Contaminare cu compusi sintetici"),
    ("H03.02.03", u"Contaminare cu radionuclizi"),
    ("H03.02.04", u"Introducerea de alte substante (de exemplu, lichide, gaze)"),
    ("H03.03", u"Macro-poluare marina (de exemplu, pungi de plastic, polistiren)"),
    ("H04", u"Poluarea aerului, poluanti raspanditi pe calea aerului"),
    ("H04.01", u"Ploi acide"),
    ("H04.02", u"Poluare cu azot(compusi azotati)"),
    ("H04.03", u"Alte forme de poluare a aerului"),
    ("H05", u"Poluarea solului si deseurile solide (cu exceptia evacuarilor)"),
    ("H05.01", u"Gunoiul si deseurile solide"),
    ("H06", u"Excesul de energie"),
    ("H06.01", u"Zgomot, poluare fonica"),
    ("H06.01.01", u"Poluarea fonica cauzata de o sursa neregulata"),
    ("H06.01.02", u"Poluarea fonica cauzata de o sursa difuza sau permanenta"),
    ("H06.02", u"Poluare luminoasa"),
    ("H06.03", u"Incalzire termica a corpurilor de apa"),
    ("H06.04", u"Modificari electromagnetice"),
    ("H06.05", u"Explorare seismica, explozii"),
    ("H07", u"Alte forme de poluare"),
    ("I", u"Specii invazive, alte probleme ale speciilor si genele"),
    ("I01", u"Specii invazive non-native(alogene)"),
    ("I02", u"Specii native(indigene) problematice"),
    ("I03", u"Organisme modificate genetic (OMG)"),
    ("I03.01", u"Poluare genetica(animale)"),
    ("I03.02", u"Poluare genetica(plante)"),
    ("J", u"Modificari ale sistemului natural"),
    ("J01", u"Focul si combaterea incendiilor"),
    ("J01.01", u"Incendii"),
    ("J01.02", u"Combaterea incendiilor naturale"),
    ("J01.03", u"Lipsa de incendii"),
    ("J02", u"Schimbari provocate de oameni in sistemele hidraulice (zone umede si (mediul marin)"),
    ("J02.01", u"Umplerea bazinelor acvatice cu pamant, indiguirea si asanarea: (generalitati"),
    ("J02.01.01", u"Polderizare - indiguire in vederea crearii unor incinte (agricole, silvice, piscicole etc."),
    ("J02.01.02", u"Recuperarea de terenuri din mare, estuare sau mlastini"),
    ("J02.01.03", u"Umplerea santurilor,zagazurilor,helesteelor, iazurilor, (mlastinilor sau gropilor"),
    ("J02.01.04", u"Recultivarea zonelor miniere"),
    ("J02.02", u"Inlaturarea de sedimente(mal)"),
    ("J02.02.01", u"Dragare/indepartarea sedimentelor limnice"),
    ("J02.02.02", u"Dragare in estuare si de coasta"),
    ("J02.03", u"Canalizare si deviere de apa"),
    ("J02.03.01", u"Deviere a apei la scara mare"),
    ("J02.03.02", u"Canalizare"),
    ("J02.04", u"Modificari de inundare"),
    ("J02.04.01", u"Inundare"),
    ("J02.04.02", u"Lipsa de inundatii"),
    ("J02.05", u"Modificarea functiilor hidrografice, generalitati"),
    ("J02.05.01", u"Modificarea debitului de apa(maree si curenti marini)"),
    ("J02.05.02", u"Modificarea structurii cursurilor de apa continentale"),
    ("J02.05.03", u"Modificarea apelor statatoare"),
    ("J02.05.04", u"Rezervoare"),
    ("J02.05.05", u"Hidrocentrale mici, stavilare"),
    ("J02.05.06", u"Modificarea gradului de expunere la valuri"),
    ("J02.06", u"Captarea apelor de suprafata"),
    ("J02.06.01", u"Captari de apa de suprafata pentru agricultura"),
    ("J02.06.02", u"Captari de apa de suprafata pentru alimentarea cu apa"),
    ("J02.06.03", u"Captari de apa de suprafata pentru industrie"),
    ("J02.06.04", u"Captari de apa de suprafata pentru productia de energie (electrica(de racire)"),
    ("J02.06.05", u"Captari de apa de suprafata pentru fermele piscicole"),
    ("J02.06.06", u"Captari de apa de suprafata pentru hidro-centrale"),
    ("J02.06.07", u"Captari de apa de suprafata pentru cariere/deschise(carbune)"),
    ("J02.06.08", u"Captari de apa de suprafata pentru navigare"),
    ("J02.06.09", u"Captari de apa de suprafata pentru transferul de apa"),
    ("J02.06.10", u"Alte captari importante de apa de suprafata"),
    ("J02.07", u"Captarea apelor subterane"),
    ("J02.07.01", u"Captari de apa subterana pentru agricultura"),
    ("J02.07.02", u"Captari de apa subterana pentru alimentarea publica cu apa"),
    ("J02.07.03", u"Captari de apa subterana pentru industrie"),
    ("J02.07.04", u"Captari de apa subterana pentru cariere/deschise(carbune)"),
    ("J02.07.05", u"Alte captari importante de apa subterana pentru agricultura"),
    ("J02.08", u"Cresterea nivelului apelor subterane/recircularea artificiala a (apelor subterane"),
    ("J02.08.01", u"Evacuari in apele subterane in scopuri de recirculare (artificiala"),
    ("J02.08.02", u"Recircularea de apa subterana la bazinul freatic de la care a (fost extrasa"),
    ("J02.08.03", u"Recircularea apei de mina"),
    ("J02.08.04", u"Other major groundwater recharge"),
    ("J02.09.", u"Intruziune de apa sarata in panza freatica"),
    ("J02.09.01", u"Intruziune de apa sarata"),
    ("J02.09.02", u"Alte intruziuni"),
    ("J02.10", u"Managementul vegetatiei acvatice si de mal in scopul drenarii"),
    ("J02.11", u"Variatiile ratei de innamolire, de descarcare, depozitarea (materialului dragat"),
    ("J02.11.01", u"Descarcarea, depozitarea materialului dragat"),
    ("J02.11.02", u"Alte modificari ale ratei de innamolire"),
    ("J02.12", u"Stavilare, diguri, plaje artificiale, generalitati"),
    ("J02.12.01", u"Lucrari de protectie a marii sau a coastei, baraje maree"),
    ("J02.12.02", u"Diguri de aparare pentru inundatii in sistemele de apa (interioare"),
    ("J02.13", u"Abandonarea gestionarii cursurilor de apa"),
    ("J02.14", u"Deteriorarea calitatii apei din cauza modificarilor antropice de (salinitate"),
    ("J02.15", u"Alte schimbari ale conditiilor hidraulice cauzate de activitati (umane"),
    ("J03", u"Alte modificari ale ecosistemelor"),
    ("J03.01", u"Reducerea sau pierderea de caracteristici specifice de habitat"),
    ("J03.01.01", u"Reducerea disponibilitatii de prada (inclusiv cadavre, (ramasite)"),
    ("J03.02", u"Reducerea conectivitatii de habitat, din cauze antropice"),
    ("J03.02.01", u"Reducerea migratiei/bariere de migratie"),
    ("J03.02.02", u"Reducerea dispersiei"),
    ("J03.02.03", u"Reducerea schimbului genetic"),
    ("J03.03", u"Reducere, lipsa sau prevenirea eroziunii"),
    ("J03.04", u"Cercetari aplicative(industriale) distructive"),
    ("K", u"Procesele naturale biotice si abiotice(fara catastrofe)"),
    ("K01", u"Procesele naturale abiotice(lente)"),
    ("K01.01", u"Eroziune"),
    ("K01.02", u"Colmatare"),
    ("K01.03", u"Secare"),
    ("K01.04", u"Inundare"),
    ("K01.05", u"Salinizarea solului"),
    ("K02", u"Evolutie biocenotica, succesiune"),
    ("K02.01", u"Schimbarea compozitiei de specii(succesiune)"),
    ("K02.02", u"Acumularea de material organic"),
    ("K02.03", u"Eutrofizare(naturala)"),
    ("K02.04", u"Acidifiere(naturala)"),
    ("K03", u"Relatii interspecifice faunistice"),
    ("K03.01", u"Competitia"),
    ("K03.02", u"Parazitism"),
    ("K03.03", u"Introducere a unor boli (patogeni microbieni)"),
    ("K03.04", u"Pradatorism"),
    ("K03.05", u"Antagonism care decurge din introducerea de specii"),
    ("K03.06", u"Antagonism cu animale domestice"),
    ("K03.07", u"Alte forme de competitie interspecifica faunistica"),
    ("K04", u"Relatii interspecifice ale florei"),
    ("K04.01", u"Competitie"),
    ("K04.02", u"Parazitism"),
    ("K04.03", u"Introducere a unor boli (patogeni microbieni)"),
    ("K04.04", u"Lipsa de agenti de polenizare"),
    ("K04.05", u"Daune cauzate de erbivore (inclusiv specii de vanat)"),
    ("K05", u"Fecunditate redusa/depresie genetica"),
    ("K05.01", u"Fertilitate redusa/depresie genetica la animale(consangvinizare)"),
    ("K05.02", u"Fertilitate redusa/depresie genetica la plante(inclusiv endogamia)"),
    ("K06", u"Alte forme sau forme mixte de competitie interspecifica a florei"),
    ("L", u"Evenimente geologice, catastrofe naturale"),
    ("L01", u"Activitate vulcanica"),
    ("L02", u"Valuri mareice, tsunami"),
    ("L03", u"Cutremure"),
    ("L04", u"Avalanse"),
    ("L05", u"Prabusiri de teren, alunecari de teren"),
    ("L06", u"Prabusiri subterane"),
    ("L07", u"Furtuni, cicloane"),
    ("L08", u"Inundatii(procese naturale)"),
    ("L09", u"Incendii(naturale)"),
    ("L10", u"Alte catastrofe naturale"),
    ("M", u"Schimbari globale"),
    ("M01", u"Schimbarea conditiilor abiotice"),
    ("M01.01", u"Schimbarea temperaturii(ex cresterea temperaturii si extremele)"),
    ("M01.02", u"Secete si precipitatii reduse"),
    ("M01.03", u"Inundatii si cresterea precipitatiilor"),
    ("M01.04", u"Schimbarea pH-ului"),
    ("M01.05", u"Modificari de debit(limnic, mareic, oceanic)"),
    ("M01.06", u"Modificarea valurilor"),
    ("M01.07", u"Modificarea nivelului marilor"),
    ("M02", u"Schimbarea conditiilor biotice"),
    ("M02.01", u"Inlocuirea si deteriorarea habitatului"),
    ("M02.02", u"Desincronizarea proceselor"),
    ("M02.03", u"Declinul sau disparitia speciilor"),
    ("M02.04", u"Migratia speciilor (nou veniti, natural)"),
    ("U", u"No threats or pressures"),
    ("X", u"Unknown threat or pressure"),
    ("XE", u"Threats and pressures from outside the EU territory"),
    ("XO", u"Threats and pressures from outside the Member State"),
]
