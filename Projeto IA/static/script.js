let dataAtual = new Date();

// Estrutura de lembretes por data (a IA vai preencher isso futuramente)
let lembretes = {};
lembretes["2026-06-14"] = [
    { texto: "entrega do projeto", prioridade: "alta" }
];


document.addEventListener("DOMContentLoaded", () => {
    renderizarCalendario();

    document.getElementById("prev").addEventListener("click", () => {
        dataAtual.setMonth(dataAtual.getMonth() - 1);
        renderizarCalendario();
    });

    document.getElementById("next").addEventListener("click", () => {
        dataAtual.setMonth(dataAtual.getMonth() + 1);
        renderizarCalendario();
    });

    carregarTarefas();
});

function renderizarCalendario() {
    const ano = dataAtual.getFullYear();
    const mes = dataAtual.getMonth();

    const primeiroDia = new Date(ano, mes, 1);
    const ultimoDia = new Date(ano, mes + 1, 0);

    const diasDiv = document.getElementById("dias");
    diasDiv.innerHTML = "";

    document.getElementById("mes-ano").innerText =
        dataAtual.toLocaleString("pt-BR", { month: "long", year: "numeric" });

    // Espaços vazios antes do primeiro dia
    for (let i = 0; i < primeiroDia.getDay(); i++) {
        diasDiv.innerHTML += "<div></div>";
    }

    // Dias do mês
    for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
        const dataCompleta = `${ano}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;

        const divDia = document.createElement("div");
        divDia.classList.add("dia");
        divDia.dataset.data = dataCompleta;
        divDia.innerHTML = `<span class="numero-dia">${dia}</span>`;

        // Se houver lembretes, mostrar bolinhas
        if (lembretes[dataCompleta]) {
            const prioridades = lembretes[dataCompleta].map(l => l.prioridade);

            if (prioridades.includes("alta")) {
                divDia.innerHTML += `<span class="bolinha bolinha-vermelha"></span>`;
            } else if (prioridades.includes("média")) {
                divDia.innerHTML += `<span class="bolinha bolinha-amarela"></span>`;
            } else {
                divDia.innerHTML += `<span class="bolinha bolinha-verde"></span>`;
            }
        }

        // Clique no dia → apenas visualização
        divDia.addEventListener("click", () => visualizarDia(dataCompleta));

        diasDiv.appendChild(divDia);
    }
}

function visualizarDia(data) {
    const lista = lembretes[data];

    if (!lista) {
        alert(`Dia ${data}\n\nNenhum lembrete.`);
        return;
    }

    let texto = `Lembretes do dia ${data}:\n\n`;

    lista.forEach(l => {
        texto += `• ${l.texto} (${l.prioridade})\n`;
    });

    alert(texto);
}

// -------------------
// Comunicação com Flask
// -------------------

async function carregarTarefas() {
    const resp = await fetch("/api/tarefas");
    const tarefas = await resp.json();

    // A IA futuramente preencherá isso
    tarefas.forEach(t => {
        if (!lembretes[t.prazo]) lembretes[t.prazo] = [];
        lembretes[t.prazo].push({
            texto: t.titulo,
            prioridade: t.prioridade
        });
    });

    renderizarCalendario();
}

async function enviarTexto() {
    const texto = document.getElementById("texto").value;

    const resp = await fetch("/api/processar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
    });

    const novas = await resp.json();

    novas.forEach(t => {
        if (!lembretes[t.prazo]) lembretes[t.prazo] = [];
        lembretes[t.prazo].push({
            texto: t.titulo,
            prioridade: t.prioridade
        });
    });

    renderizarCalendario();
    document.getElementById("texto").value = "";
}
