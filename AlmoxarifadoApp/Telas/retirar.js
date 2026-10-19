// retirar.js
// Monta a página "Retirar Estoque" inteira via JavaScript.
// Uso: crie um HTML mínimo (ver abaixo) e inclua <script src="static/retirar.js"></script> no final do <body>.
 
// ---------- Utilitário ----------
function criar(tag, atributos = {}, filhos = []) {
  const el = document.createElement(tag);
  for (const [chave, valor] of Object.entries(atributos)) {
    if (chave === "texto") el.textContent = valor;
    else el.setAttribute(chave, valor);
  }
  filhos.forEach((f) => el.appendChild(f));
  return el;
}
 
function campo(classeColuna, id, name, rotulo) {
  return criar("div", { class: classeColuna }, [
    criar("label", { for: id, class: "form-label", texto: rotulo }),
    criar("input", { type: "text", name: name, class: "form-control", id: id }),
  ]);
}
 
// ---------- <head> ----------
document.documentElement.lang = "en";
document.title = "Retirar Estoque";
 
const head = document.head;
head.appendChild(criar("meta", { charset: "UTF-8" }));
head.appendChild(
  criar("meta", { name: "viewport", content: "width=device-width, initial-scale=1.0" })
);
head.appendChild(criar("link", { rel: "stylesheet", href: "static/retirar.css" }));
head.appendChild(criar("link", { rel: "icon", type: "image/x-icon", href: "static/aba.ico" }));
head.appendChild(
  criar("link", {
    href: "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
    rel: "stylesheet",
    integrity: "sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB",
    crossorigin: "anonymous",
  })
);
 
// ---------- <body> ----------
const cabecalho = criar("header", { id: "cabecalho" }, [
  criar("h1", { texto: "Retirar itens do estoque" }),
  criar("p", { texto: "Controle de estoque" }),
]);
 
const selectOperacao = criar("select", { id: "retire", name: "operacao" }, [
  criar("option", { selected: "", value: "Entrada", texto: "Entrada" }),
  criar("option", { value: "Saida", texto: "Saída" }),
]);
 
const botao = criar("button", {
  id: "botao_cadastro",
  type: "submit",
  class: "btn btn-primary",
  texto: "Movimentar",
});
 
const form = criar("form", { id: "Quadro", action: "/retirar", method: "POST" }, [
  selectOperacao,
  campo("col-md-6", "nome_item", "nomeItem", "Nome do Item"),
  campo("col-md-6", "categoria", "categoria", "Categoria"),
  campo("col-12", "funcao", "funcao", "Função"),
  campo("col-12", "quantidade", "quantidade", "Quantidade"),
  criar("div", { class: "col-12" }, [botao]),
]);
 
const formularioRetirar = criar("div", { id: "formulario_retirar" }, [form]);
 
document.body.appendChild(cabecalho);
document.body.appendChild(formularioRetirar);