let dataAtual = new Date();

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
        diasDiv.innerHTML += `<div>${dia}</div>`;
    }
}

// -------------------
// Comunicação com Flask
// -------------------

async function carregarTarefas() {
    const resp = await fetch("/api/tarefas");
    const tarefas = await resp.json();
    console.log("Tarefas carregadas:", tarefas);
}

async function enviarTexto() {
    const texto = document.getElementById("texto").value;

    const resp = await fetch("/api/processar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
    });

    const novas = await resp.json();
    console.log("Tarefas novas:", novas);

    document.getElementById("texto").value = "";
}
