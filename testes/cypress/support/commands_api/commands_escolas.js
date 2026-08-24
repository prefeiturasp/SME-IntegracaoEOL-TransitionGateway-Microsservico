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

Cypress.Commands.add("postEscolas", (valido) => {
  let lista =
    valido === true
      ? `["${Cypress.env("UE_CODIGO")}"]`
      : `["${Cypress.env("UE_CODIGO_INEXISTENTE")}"]`;
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/escolas/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
    },
    body: lista,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaSubprefeituras", (codigoUe) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/subprefeituras/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getFuncionariosPorCargo", (codigoUe, codigoCargo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/funcionarios/cargos/${codigoCargo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getFuncionariosPorCargos",
  (codigoUe, cargos, codigoDre) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/escolas/${codigoUe}/funcionarios/cargos/?cargos=${cargos}&codigo_dre=${codigoDre}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getFuncionariosPorFuncoesAtividades",
  (codigoUe, funcoesAtividades, codigoDre) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/escolas/${codigoUe}/funcionarios/funcoes-atividades/?funcoes_atividades=${funcoesAtividades}&codigo_dre=${codigoDre}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getFuncionariosPorFuncaoAtividade",
  (codigoUe, codigoFuncaoAtividade) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/escolas/${codigoUe}/funcionarios/funcoes-atividades/${codigoFuncaoAtividade}/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getFuncionariosPorFuncoesExternas",
  (codigoUe, funcoes, codigoDre) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/escolas/${codigoUe}/funcionarios/funcoes-externas/?funcoes=${funcoes}&codigo_dre=${codigoDre}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getFuncionariosPorFuncaoExterna",
  (codigoUe, codigoFuncaoExterna) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/escolas/${codigoUe}/funcionarios/funcoes-externas/${codigoFuncaoExterna}/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getMatriculasEscolaQuantidades", (codigoUe) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/matriculas/escolas/${codigoUe}/quantidades`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getMatriculasEscolaDreQuantidades", (dreCodigo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/matriculas/escolas/dre/${dreCodigo}/quantidades`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaAlunosQuantidade", (codigoUe) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/alunos/quantidade/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaAlunoMatriculas", (codigoUe, codigoAluno) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/alunos/${codigoAluno}/matriculas/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getModalidadesEnsino", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/modalidades_ensino`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaSalas", (codigoUe, tipoSala, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/escolas/${codigoUe}/salas/${tipoSala}/anos_letivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaTurmas", (codigoUe, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/turmas/anos_letivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaTurmasSondagem", (codigoUe, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/escolas/${codigoUe}/turmasSondagem/anos_letivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getEscolaProfessores", (codigoUe, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/escolas/${codigoUe}/professores/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
