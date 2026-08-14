Cypress.Commands.add("getAlunoInformacoes", (valor) => {
  let codigo = valor === true ? `${Cypress.env("CODIGO_ALUNO")}` : "010101001";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/${codigo}/informacoes`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunoNecessidadesEspeciais", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/${Cypress.env("CODIGO_ALUNO")}/necessidades-especiais`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunosPorCodigos", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/alunos`,
    qs: { codigos_aluno: [Cypress.env("CODIGO_ALUNO")] },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunosPapAnoCorrente", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/pap/ano-corrente/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunosPapPorAnoLetivo", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/pap/ano-letivo/${Cypress.env("ANO_LETIVO")}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunoSrmPaee", (valor) => {
  let codigo = valor === true ? `${Cypress.env("CODIGO_ALUNO")}` : "0";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/srm-paee/aluno/${codigo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunoTurmas", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/${Cypress.env("CODIGO_ALUNO")}/turmas`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmasPapPorAnoLetivoEEscola", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/turmas-pap/${Cypress.env("ANO_LETIVO")}/ues/${Cypress.env("CODIGO_ESCOLA")}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesTurmasProgramaAluno", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/${Cypress.env("CODIGO_ALUNO")}/turmas-programa/${Cypress.env("ANO_LETIVO")}/componentes-curriculares/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getVerificacaoAlunosTurmasPap", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/alunos/alunos-pap/${Cypress.env("ANO_LETIVO")}/`,
    qs: { codigos_alunos: [Cypress.env("CODIGO_ALUNO")] },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getAlunosMatriculadosQuantidade", (ano) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/ano-letivo/${ano}/matriculados/quantidade`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getAlunosMatriculados",
  (ano, componentesCurriculares) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/v1/alunos/ano-letivo/${ano}/matriculados?componentes_curriculares=${componentesCurriculares}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getAlunosPorCodigo", (ano, codigoAluno) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/v1/alunos/anoLetivo/${ano}/alunos?codigos_aluno=${codigoAluno}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getDadosAcompanhamentoEscolar", (queryParams = "") => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/dados-acompanhamento-escolar${queryParams}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getResponsaveis", (queryParams = "") => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/responsaveis${queryParams}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getResponsavelResumido", (cpf) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/responsaveis/${cpf}/resumido`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

/////NOVOS

Cypress.Commands.add("getAlunosAtivosTurma", (codigoTurma) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/alunos/turmas/${codigoTurma}/ativos`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getAlunosAtivosTurmaPorData",
  (codigoTurma, dataReferenciaFim) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/v1/alunos/turmas/${codigoTurma}/ativos/${dataReferenciaFim}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmasAlunoPorUeAnoLetivo",
  (codigoUe, anoLetivo, nomeAluno) => {
    let query = nomeAluno ? `?nome_aluno=${nomeAluno}` : "";
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/v1/alunos/ues/${codigoUe}/anosLetivos/${anoLetivo}${query}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);
