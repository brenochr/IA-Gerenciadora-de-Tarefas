let dataAtual = new Date();

// Estrutura de lembretes por data (a IA vai preencher isso futuramente)
let lembretes = {};

// EXEMPLO MANUAL PARA TESTE
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

    // Seleciona automaticamente o dia atual no painel
    const hoje = new Date();
    const dataHoje = `${hoje.getFullYear()}-${String(hoje.getMonth()+1).padStart(2,"0")}-${String(hoje.getDate()).padStart(2,"0")}`;
    selecionarDia(dataHoje);
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

    const hoje = new Date();
    const hojeLimpo = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());

    // Espaços vazios antes do primeiro dia
    for (let i = 0; i < primeiroDia.getDay(); i++) {
        diasDiv.innerHTML += "<div></div>";
    }

    // Dias do mês
    for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
        const dataCompleta = `${ano}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
        const dataDia = new Date(ano, mes, dia);

        const divDia = document.createElement("div");
        divDia.classList.add("dia");
        divDia.dataset.data = dataCompleta;
        divDia.innerHTML = `<span class="numero-dia">${dia}</span>`;

        // Marcar dias passados
        if (dataDia < hojeLimpo) {
            divDia.classList.add("dia-passado");
        } else {
            divDia.addEventListener("click", () => selecionarDia(dataCompleta));
        }

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

        diasDiv.appendChild(divDia);
    }
}

// Atualiza o painel lateral com a data selecionada
function selecionarDia(data) {
    const painelData = document.getElementById("painel-data");
    const lista = document.getElementById("lista-lembretes");
    const semLembretes = document.getElementById("sem-lembretes");

    // CORREÇÃO DO BUG DO DIA ANTERIOR
    const [ano, mes, dia] = data.split("-").map(Number);
    const dataObj = new Date(ano, mes - 1, dia);

    painelData.innerText = dataObj.toLocaleDateString("pt-BR", {
        weekday: "long",
        day: "2-digit",
        month: "long",
        year: "numeric"
    });

    lista.innerHTML = "";

    if (!lembretes[data] || lembretes[data].length === 0) {
        semLembretes.style.display = "block";
        return;
    }

    semLembretes.style.display = "none";

    lembretes[data].forEach(l => {
        const li = document.createElement("li");
        li.classList.add("lembrete-item");

        const bolinha = document.createElement("div");
        bolinha.classList.add("bolinha-lista");

        if (l.prioridade === "alta") bolinha.classList.add("bolinha-vermelha");
        else if (l.prioridade === "média") bolinha.classList.add("bolinha-amarela");
        else bolinha.classList.add("bolinha-verde");

        li.appendChild(bolinha);
        li.appendChild(document.createTextNode(l.texto));

        lista.appendChild(li);
    });
}

// -------------------
// Comunicação com Flask
// -------------------

async function carregarTarefas() {
    const resp = await fetch("/api/tarefas");
    const tarefas = await resp.json();

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
