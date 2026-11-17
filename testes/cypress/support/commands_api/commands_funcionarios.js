const headersPadrao = () => ({
  accept: "application/json",
  "Content-Type": "application/json",
  [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
});

Cypress.Commands.add("getNomeServidor", (valor) => {
  let rf = valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/nome-servidor/${rf}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionarioNomeEol", (valor) => {
  let rf = valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/nome-usuario-eol/${rf}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postBuscarPorListaRf", (valor) => {
  let rf =
    valor === true
      ? `${Cypress.env("UE_TURMAS_CODIGO")}`
      : ["242257", "212121"];
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/funcionarios/BuscarPorListaRF`,
    headers: headersPadrao(),
    body: rf,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionarioDadosSigpae", (codigoRf) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/DadosSigpae/${codigoRf}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getFuncionarioAtribuicaoCargo",
  (registroFuncional, codigoCargo) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/funcionarios/atribuicao/${registroFuncional}/cargo/${codigoCargo}`,
      headers: headersPadrao(),
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getFuncionarioCargos", (registroFuncional) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/cargo/${registroFuncional}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionariosPorCodigoCargo", (codigoCargo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/cargos/${codigoCargo}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionarioExterno", (cpf) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/funcionario-externo/${cpf}`,
    headers: headersPadrao(),
    failOnStatusCode: false,
  });
});
