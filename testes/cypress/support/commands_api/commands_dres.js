// GET - Listagem de DREs
Cypress.Commands.add("getDREsLista", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// POST -
Cypress.Commands.add("postDREsLista", (valor) => {
  let listaCodigos =
    valor === true ? `${Cypress.env("DRE_LISTA_CODIGOS")}` : "[0]";
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/DREs/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN":
        "p79VpPZPLy1hrkXUx7EIOUlbvQZh8aCKpa2fE2omOAaIJBBAbpeUwBDQu9lS5JTY",
    },
    body: `${listaCodigos}`,
    failOnStatusCode: false,
  });
});

// GET - Detalhe de DRE
Cypress.Commands.add("getDREDetalhe", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Escolas de uma DRE
Cypress.Commands.add("getDREsEscolas", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/escola/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Escolas de uma DRE por tipo de unidade
Cypress.Commands.add("getDREsEscolasPorTipo", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  let tipoUe = 1;
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/escolas/${tipoUe}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Subprefeituras de uma DRE
Cypress.Commands.add("getDREsSubprefeituras", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/subprefeituras/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - UEs de uma DRE
Cypress.Commands.add("getDREsUEs", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/ues/`,
    headers: {
      accept: "*/*",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Unidades de uma DRE
Cypress.Commands.add("getDREsUnidades", (valor) => {
  let codigo = valor === true ? `${Cypress.env("DRE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigo}/unidades/`,
    headers: {
      accept: "*/*",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolasSigpaePorDre", (codigoEolDre) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigoEolDre}/escola/Sigpae/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getUnidadesCodigoIntegracaoPorDre", (codigoEolDre) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/DREs/${codigoEolDre}/unidades/codigo-integracao/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
