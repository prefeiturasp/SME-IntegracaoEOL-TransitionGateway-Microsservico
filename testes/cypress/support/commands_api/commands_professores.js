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

Cypress.Commands.add(
  "getProfessoresAutoComplete",
  (anoLetivo, dreCodigo, ueCodigo, nome) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/professores/${anoLetivo}/AutoComplete/${dreCodigo}/`,
      qs: {
        ue_id: ueCodigo,
        nome: nome,
      },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("postProfessoresBuscarPorListaRF", (anoLetivo, valido) => {
  let listaRF =
    valido === true
      ? `["${Cypress.env("REGISTRO_FUNCIONAL")}"]`
      : `["${Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")}"]`;
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/professores/${anoLetivo}/BuscarPorListaRF/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
    },
    body: listaRF,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getProfessorBuscarPorRF",
  (registroFuncional, anoLetivo) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/BuscarPorRf/${anoLetivo}/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getProfessorBuscarPorRFDreUe",
  (registroFuncional, anoLetivo, dreCodigo, ueCodigo) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/BuscarPorRfDreUe/${anoLetivo}/`,
      qs: {
        dre_id: dreCodigo,
        ue_id: ueCodigo,
      },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "postProfessorTurmasPorDisciplina",
  (registroFuncional, disciplinaId, valido) => {
    let listaTurma =
      valido === true
        ? `["${Cypress.env("TURMA_CODIGO")}"]`
        : `["${Cypress.env("TURMA_CODIGO_INEXISTENTE")}"]`;
    return cy.request({
      method: "POST",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/disciplina/${disciplinaId}/turmas/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
        "Content-Type": "application/json",
        "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
      },
      body: listaTurma,
      failOnStatusCode: false,
    });
  },
);
