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

Cypress.Commands.add("getProfessorEhEmei", (valido) => {
  const rf =
    valido === true
      ? `${Cypress.env("REGISTRO_FUNCIONAL_EMEI")}`
      : `${Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")}`;

  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/professores/${rf}/ehEmei/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getProfessorTurmas", (valido) => {
  const rf =
    valido === true
      ? `${Cypress.env("REGISTRO_FUNCIONAL")}`
      : `${Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")}`;

  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/professores/${rf}/turmas/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getProfessorTurmasPorAnoLetivo", (anoLetivo, valido) => {
  const rf =
    valido === true
      ? `${Cypress.env("REGISTRO_FUNCIONAL")}`
      : `${Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")}`;

  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/professores/${rf}/turmas/anos_letivos/${anoLetivo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getProfessorTurmasNaEscola", (anoLetivo, valido) => {
  const rf =
    valido === true
      ? `${Cypress.env("REGISTRO_FUNCIONAL")}`
      : `${Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")}`;
  const escola =
    valido === true
      ? `${Cypress.env("UE_CODIGO")}`
      : `${Cypress.env("UE_CODIGO_INEXISTENTE")}`;

  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/professores/${rf}/escolas/${escola}/turmas/anos_letivos/${anoLetivo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmasProfessoresNaEscola", (anoLetivo, valido) => {
  const escola =
    valido === true
      ? `${Cypress.env("UE_CODIGO")}`
      : `${Cypress.env("UE_CODIGO_INEXISTENTE")}`;

  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/professores/escolas/${escola}/turmas/anos_letivos/${anoLetivo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getProfessorAtribuicaoPorData",
  (registroFuncional, codigoTurma, data, dataValida) => {
    const valorData = dataValida === true ? data : "2026-99-99";

    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/turmas/${codigoTurma}/atribuicao/verificar/data/`,
      qs: { dataConsulta: valorData },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getProfessorStatusAtribuicao",
  (registroFuncional, codigoTurma) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/turmas/${codigoTurma}/atribuicao/status/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getProfessorVerificarAtribuicaoDisciplina",
  (registroFuncional, codigoTurma, disciplinaId, data) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${registroFuncional}/turmas/${codigoTurma}/disciplinas/${disciplinaId}/atribuicao/verificar/datas`,
      qs: { data },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getAtribuicoesTurmaDisciplinaDataIso",
  (codigoTurma, disciplinaId, data) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/professores/${codigoTurma}/disciplinas/${disciplinaId}/atribuicao/data-iso`,
      qs: { data },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);
