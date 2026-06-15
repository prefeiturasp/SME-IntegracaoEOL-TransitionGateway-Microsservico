Cypress.Commands.add("getFuncionarioAtivo", (valor) => {
  let ativo =
    valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/acessos/funcionario-ativo/${ativo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

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

Cypress.Commands.add("getProfessorValidade", (valor) => {
  let validade =
    valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/professores/${validade}/validade/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getProfessorPorRF", (valor) => {
  let rf_prof =
    valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";

  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/professores/${rf_prof}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
