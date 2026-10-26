Cypress.Commands.add("getTurmaDados", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${Cypress.env("TURMA_CODIGO")}/dados`,
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
    url: `${Cypress.env("API_URL")}/api/turmas/listar-turmas`,
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
    url: `${Cypress.env("API_URL")}/api/turmas/turmas-programa`,
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
    url: `${Cypress.env("API_URL")}/api/turmas/turmas-regulares`,
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

Cypress.Commands.add(
  "getAlunoTurmaConsideraInativos",
  (
    codigoTurma = Cypress.env("TURMA_CODIGO"),
    codigoAluno = Cypress.env("CODIGO_ALUNO"),
    consideraInativos = "true",
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/aluno/${codigoAluno}/considera-inativos/${consideraInativos}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getAlunoMatriculasTurma",
  (
    codigoTurma = Cypress.env("TURMA_CODIGO"),
    codigoAluno = Cypress.env("CODIGO_ALUNO"),
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/aluno/${codigoAluno}/matriculas`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getAlunosAtivosDataAulaTicks",
  (
    codigoTurma = Cypress.env("TURMA_CODIGO"),
    dataTicks = "639031104000000000",
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/alunos-ativos/data-aula-ticks/${dataTicks}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmaCalculoFrequencia",
  (codigoTurma = Cypress.env("TURMA_CODIGO")) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/calculo-frequencia`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmaConsideraInativos",
  (codigoTurma = Cypress.env("TURMA_CODIGO"), consideraInativos = "true") => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/considera-inativos/${consideraInativos}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmaDataMatriculaTicks",
  (
    codigoTurma = Cypress.env("TURMA_CODIGO"),
    dataMatriculaTicks = "639059616000000000",
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/data-matricula-ticks/${dataMatriculaTicks}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmaRedisMultplex",
  (codigoTurma = Cypress.env("TURMA_CODIGO")) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/redis-Multplex`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getAlunoComponentesCurricularesPorTurma",
  (
    anoLetivo = Cypress.env("ANO_LETIVO"),
    codigoAluno = Cypress.env("CODIGO_ALUNO"),
    componenteCurricularCodigo = Cypress.env("COMPONENTE_CURRICULAR"),
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/anos-letivos/${anoLetivo}/alunos/${codigoAluno}/componentes-curriculares/${componenteCurricularCodigo}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getAlunoTurmasRegularesPorAnoLetivo",
  (
    anoLetivo = Cypress.env("ANO_LETIVO"),
    codigoAluno = Cypress.env("CODIGO_ALUNO"),
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/anos-letivos/${anoLetivo}/alunos/${codigoAluno}/regulares`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getProfessorTurmasHistoricasGeral",
  (
    anoLetivo = Cypress.env("ANO_LETIVO"),
    professorRf = Cypress.env("REGISTRO_FUNCIONAL"),
  ) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/anos-letivos/${anoLetivo}/professor/${professorRf}/turmas-historicas-geral`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmasSincronizacoesAnosLetivos",
  (codigoUe, anoLetivo) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/ue/${codigoUe}/sincronizacoes-institucionais/anos-letivos`,
      qs: {
        anosLetivosVigente: anoLetivo,
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
  "getUeTurmaSincronizacoesInstitucionais",
  (codigoUe, codigoTurma) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/ues/${codigoUe}/turmas/${codigoTurma}/sincronizacoes-institucionais`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getTurmasAlunosAnoLetivo", (codigoUe, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${codigoUe}/alunos/anosLetivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getUeTurmaSincronizacoesInstitucionais",
  (codigoUe, codigoTurma) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/ues/${codigoUe}/turmas/${codigoTurma}/sincronizacoes-institucionais`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getTurmasAlunosAnoLetivo", (codigoUe, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${codigoUe}/alunos/anosLetivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmaSemRedis", (codigoTurma) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/sem-redis`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmasItinerarioEnsinoMedio", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/itinerario/ensino-medio`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getTurmasComponentes",
  (codigoUe, modalidade, anoLetivo, consideraHistorico) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/turmas/ues/${codigoUe}/modalidades/${modalidade}/anos/${anoLetivo}/componentes`,
      qs: {
        consideraHistorico: consideraHistorico,
      },
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("getTurmaAlunosPorAnoLetivo", (codigoTurma, anoLetivo) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/alunos/anosLetivos/${anoLetivo}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmaTodosAlunos", (codigoTurma) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/todos-alunos`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getTurmasAluno", (codigoAluno) => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/turmas/alunos/${codigoAluno}`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add(
  "getTurmaAcompanhamentoEscolarTodosAlunos",
  (codigoTurma) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env("API_URL")}/api/turmas/${codigoTurma}/acompanhamento-escolar/todos-alunos`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add(
  "getTurmasTodosAlunosFiltros",
  (anoTurma, modalidade, anoLetivo, dreCodigo, dataInicio, dataFim) => {
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/turmas/todos-alunos/ano-turma/${anoTurma}/modalidade/${modalidade}/ano-letivo/${anoLetivo}/dre/${dreCodigo}/inicio/${dataInicio}/fim/${dataFim}`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);
