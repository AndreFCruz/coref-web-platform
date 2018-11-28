text_examples = {
    'es': [
        "En [la hierba de [Wimbledon]], [Gran_Bretaña, con [[Tim_Henman], [Greg_Rusedski] y los jóvenes [[Arvind_Parmar] y [Barry_Cowan]]]],] buscará seguir una temporada más en [la elite del [tenis mundial] frente a [Ecuador], encabezada por [Nicolás_Lapentti]].",
        "[El doble [que] se enfrentará a la pareja Sandon_Stolle-Mark_Woodforde] será el formado por [[\"Guga\"] y [Jaime_Oncins]].",
        "[Australia, actual campeona del [torneo],] intentará aprovechar [[su] teórica ventaja] en [la hierba, en [la que] [los luchadores jugadores brasileños], salvo [el \"todoterreno\" Gustavo Kuerten], no se adaptan bien].",
        "[Brasil] buscará a_partir_de mañana [el pase a [su] primera final de la [Copa_Davis]] ante [los vigentes campeones, los australianos,] y sobre [la incómoda hierba del [ANZ_Stadium_de_Brisbane]]."
    ],
    'pt': [
        "Segundo [fontes aeroportuárias], [os membros da [tripulação]] eram de nacionalidade russa. [O avião] explodiu e [se] incendiou, acrescentou [o porta-voz da [ONU] em [Kinshasa]], [Jean-Tobias_Okala]. [O porta-voz] informou que [o avião], [um Soviet] Antonov-28 de fabricação ucraniana e propriedade de [uma companhia congolesa], a [Trasept_Congo], também levava [uma carga de minerais]."
    ]
}

function encodeForAjax(data) {
    return Object.keys(data).map(function(k) {
        return encodeURIComponent(k) + '=' + encodeURIComponent(data[k])
    }).join('&');
}

function submitDocumentForm(event) {
    event.preventDefault();

    let text = document.querySelector('#documentInput').value;
    if (!text || 0 === text.trim().length) {
        console.warn('Empty string submitted.');
        return false;
    }

    let model = document.querySelector('#modelSelection').options.selectedIndex;
    let automaticMentionDetection = document.querySelector('#automaticMentionDetection').checked;

    let request = new XMLHttpRequest();
    request.onload = showFormResult;
    request.open('post', 'api/clusters', true) // async == true
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.send(encodeForAjax({
        document: text,
        model: model,
        automaticMentionDetection: automaticMentionDetection
    }));
}

function showFormResult() {
    let data = JSON.parse(this.responseText);
    
    let mentions = data.mentions;
    let mentionsArea = document.querySelector('#mentions');
    mentionsArea.value = mentions.map((m, idx) =>
        (idx+1).toString() + ': "' + m + '"')
        .join(';\n')

    let clusters = data.clusters;
    let clustersArea = document.querySelector('#clusters');
    clustersArea.value = clusters_to_user_friendly_string(clusters, mentions);
}

function clusters_to_user_friendly_string(clusters, mentions) {
    return clusters.map(
        (cluster, idx) => (idx+1).toString() + ': '
            + cluster.map(i => '"' + mentions[i] + '"').join(', ')
    ).join(';\n---\n');
}

function randomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function showRandomExample() {
    textarea = document.querySelector('#documentInput');
    model = document.querySelector('#modelSelection');
    if (Math.random() < 0.5) { // PT example
        model.options.selectedIndex = 0; // 0th -> PT
        textarea.value = randomElement(text_examples['pt']);
    } else { // ES example
        model.options.selectedIndex = 1; // 1st -> ES
        textarea.value = randomElement(text_examples['es']);
    }
}

window.onload = function() {
    // Set-Up Document Form
    document.querySelector('#doc-form').onsubmit = submitDocumentForm;
    showRandomExample();
}