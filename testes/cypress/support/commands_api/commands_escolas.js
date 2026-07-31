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

// GET - Unidade EOL por código
Cypress.Commands.add("getEscolaUnidadeEol", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/unidade-eol/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Sincronizações institucionais da escola
Cypress.Commands.add("getEscolaSincronizacoesInstitucionais", (valor) => {
  let codigo = valor === true ? `${Cypress.env("UE_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigo}/sincronizacoes-institucionais/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// POST - Unidades parceiras
Cypress.Commands.add("postEscolasUnidadesParceiras", (valor) => {
  let lista = valor === true ? '["092797"]' : '["000000"]';
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/escolas/unidades-parceiras/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN":
        "NWWRDQY2fawbtjjDFiUDjO8Ufv9IIT4qrpKiF7bCVwHZNONnBzNXxERytrzO2f9x",
    },
    body: `${lista}`,
    failOnStatusCode: false,
  });
});

// GET - Todas as unidades
Cypress.Commands.add("getEscolaTodasUnidades", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/todas-unidades/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

// GET - Tipos de unidade de educação
Cypress.Commands.add("getTiposUnidadeEducacao", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/tipos_unidade_educacao/`,
    headers: {
      accept: "*/*",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
