let calendario;

document.addEventListener("DOMContentLoaded", async function () {
    const calendarEl = document.getElementById("calendario");

    calendario = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "pt-br",
        events: []
    });

    calendario.render();

    await carregarTarefas();
});


async function carregarTarefas() {
    const resp = await fetch("/api/tarefas");
    const tarefas = await resp.json();

    tarefas.forEach(t => {
        calendario.addEvent({
            title: t.titulo,
            start: t.prazo,
            allDay: true
        });
    });
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
        calendario.addEvent({
            title: t.titulo,
            start: t.prazo,
            allDay: true
        });
    });

    document.getElementById("texto").value = "";
}
