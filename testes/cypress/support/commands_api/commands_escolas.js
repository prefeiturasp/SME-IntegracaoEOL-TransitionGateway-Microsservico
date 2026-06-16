Cypress.Commands.add("getEscolaDetalhe", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaDadosCompletos", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/dados/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaTipos", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/tiposEscolas/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaFuncionarios", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigo}/funcionarios/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaEquipamentos", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/equipamentos/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
Cypress.Commands.add("getEscolaDetalhe", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaDadosCompletos", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/dados/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaTipos", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/tiposEscolas/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaFuncionarios", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigo}/funcionarios/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaEquipamentos", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/equipamentos/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
