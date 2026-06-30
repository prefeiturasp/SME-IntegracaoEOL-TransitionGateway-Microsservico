Cypress.Commands.add("getTurmaDados", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${Cypress.env("TURMA_CODIGO")}/dados/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postListarTurmas", () => {
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/turmas/listar-turmas/`,
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    body: Cypress.env("UE_TURMAS_CODIGO"),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postTurmasPrograma", () => {
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/turmas/turmas-programa/`,
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    body: Cypress.env("UE_TURMAS_CODIGO"),
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postTurmasRegulares", () => {
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/turmas/turmas-regulares/`,
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    body: Cypress.env("UE_TURMAS_CODIGO"),
    log: true,
    failOnStatusCode: false,
  });
});
