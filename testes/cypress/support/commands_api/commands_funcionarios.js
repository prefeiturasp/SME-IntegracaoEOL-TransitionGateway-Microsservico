Cypress.Commands.add("getNomeServidor", (valor) => {
  let rf = valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/nome-servidor/${rf}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionarioNomeEol", (valor) => {
  let rf = valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/funcionarios/nome-usuario-eol/${rf}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postBuscarPorListaRf", () => {
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/funcionarios/BuscarPorListaRF/`,
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    body: Cypress.env("REGISTRO_FUNCIONAL"),
    failOnStatusCode: false,
  });
});
