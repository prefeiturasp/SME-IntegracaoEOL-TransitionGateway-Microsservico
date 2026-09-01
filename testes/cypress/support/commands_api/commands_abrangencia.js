Cypress.Commands.add("getAbrangenciaEstruturaVigente", (codigoDre) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/abrangencia/estrutura-vigente/${codigoDre}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postAbrangenciaEstruturaVigente", (valido) => {
  let filtroTurmas =
    valido === true
      ? Cypress.env("ABRANGENCIA_FILTRO_TURMAS")
      : Cypress.env("ABRANGENCIA_FILTRO_TURMAS_INEXISTENTE");
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/abrangencia/estrutura-vigente/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
    },
    body: filtroTurmas,
    failOnStatusCode: false,
  });
});
