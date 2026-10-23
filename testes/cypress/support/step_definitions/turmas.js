import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

Given("que possuo acesso à API de turmas", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
});

When("realizo consulta de dados da turma", () => {
  cy.getTurmaDados().as("response");
});

When("realizo listagem de turmas por lista de códigos", () => {
  cy.postListarTurmas().as("response");
});

When("realizo consulta de turmas programa por lista de códigos", () => {
  cy.postTurmasPrograma().as("response");
});

When("realizo consulta de turmas regulares por lista de códigos", () => {
  cy.postTurmasRegulares().as("response");
});

When("realizo consulta de considera inativos do aluno na turma", () => {
  cy.getAlunoTurmaConsideraInativos().as("response");
});

When(
  "realizo consulta de considera inativos do aluno na turma com turma inválida",
  () => {
    cy.getAlunoTurmaConsideraInativos("abc").as("response");
  },
);

When(
  "realizo consulta de considera inativos do aluno na turma com aluno inválido",
  () => {
    cy.getAlunoTurmaConsideraInativos(Cypress.env("TURMA_CODIGO"), "abc").as(
      "response",
    );
  },
);

When(
  "realizo consulta de considera inativos do aluno na turma com flag inválida",
  () => {
    cy.getAlunoTurmaConsideraInativos(
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("CODIGO_ALUNO"),
      "talvez",
    ).as("response");
  },
);

When(
  "realizo consulta de considera inativos do aluno na turma com aluno inexistente",
  () => {
    cy.getAlunoTurmaConsideraInativos(
      Cypress.env("TURMA_CODIGO"),
      "9999999",
    ).as("response");
  },
);

When("realizo consulta de matriculas do aluno na turma", () => {
  cy.getAlunoMatriculasTurma().as("response");
});

When(
  "realizo consulta de matriculas do aluno na turma com turma inválida",
  () => {
    cy.getAlunoMatriculasTurma("abc").as("response");
  },
);

When(
  "realizo consulta de matriculas do aluno na turma com aluno inválido",
  () => {
    cy.getAlunoMatriculasTurma(Cypress.env("TURMA_CODIGO"), "abc").as(
      "response",
    );
  },
);

When(
  "realizo consulta de matriculas do aluno na turma com aluno inexistente",
  () => {
    cy.getAlunoMatriculasTurma(Cypress.env("TURMA_CODIGO"), "9999999").as(
      "response",
    );
  },
);

When("realizo consulta de alunos ativos por data de aula", () => {
  cy.getAlunosAtivosDataAulaTicks().as("response");
});

When(
  "realizo consulta de alunos ativos por data de aula com ticks inválidos",
  () => {
    cy.getAlunosAtivosDataAulaTicks(Cypress.env("TURMA_CODIGO"), "abc").as(
      "response",
    );
  },
);

When(
  "realizo consulta de alunos ativos por data de aula com turma inexistente",
  () => {
    cy.getAlunosAtivosDataAulaTicks("9999999").as("response");
  },
);

When("realizo consulta de calculo de frequencia da turma", () => {
  cy.getTurmaCalculoFrequencia().as("response");
});

When(
  "realizo consulta de calculo de frequencia da turma com turma inexistente",
  () => {
    cy.getTurmaCalculoFrequencia("9999999").as("response");
  },
);

When("realizo consulta de considera inativos da turma", () => {
  cy.getTurmaConsideraInativos().as("response");
});

When(
  "realizo consulta de considera inativos da turma com turma inválida",
  () => {
    cy.getTurmaConsideraInativos("abc").as("response");
  },
);

When(
  "realizo consulta de considera inativos da turma com turma inexistente",
  () => {
    cy.getTurmaConsideraInativos("9999999").as("response");
  },
);

When("realizo consulta de data de matricula por ticks", () => {
  cy.getTurmaDataMatriculaTicks().as("response");
});

When("realizo consulta de data de matricula por ticks inválidos", () => {
  cy.getTurmaDataMatriculaTicks(Cypress.env("TURMA_CODIGO"), "0").as(
    "response",
  );
});

When(
  "realizo consulta de data de matricula por ticks da turma inexistente",
  () => {
    cy.getTurmaDataMatriculaTicks("9999999").as("response");
  },
);

When("realizo consulta de dados redis multplex da turma", () => {
  cy.getTurmaRedisMultplex().as("response");
});

When("realizo consulta de dados redis multplex da turma inexistente", () => {
  cy.getTurmaRedisMultplex("9999999").as("response");
});

When("realizo consulta de componentes curriculares do aluno da turma", () => {
  cy.getAlunoComponentesCurricularesPorTurma().as("response");
});

When(
  "realizo consulta de componentes curriculares do aluno da turma com aluno inexistente",
  () => {
    cy.getAlunoComponentesCurricularesPorTurma(
      Cypress.env("ANO_LETIVO"),
      "9999999",
    ).as("response");
  },
);

When("realizo consulta de turmas regulares do aluno por ano letivo", () => {
  cy.getAlunoTurmasRegularesPorAnoLetivo().as("response");
});

When(
  "realizo consulta de turmas regulares do aluno por ano letivo com aluno inválido",
  () => {
    cy.getAlunoTurmasRegularesPorAnoLetivo(Cypress.env("ANO_LETIVO"), "abc").as(
      "response",
    );
  },
);

When(
  "realizo consulta de turmas regulares do aluno por ano letivo com aluno inexistente",
  () => {
    cy.getAlunoTurmasRegularesPorAnoLetivo(
      Cypress.env("ANO_LETIVO"),
      "9999999",
    ).as("response");
  },
);

When("realizo consulta de turmas historicas gerais do professor", () => {
  cy.getProfessorTurmasHistoricasGeral().as("response");
});

When(
  "realizo consulta de turmas historicas gerais do professor inexistente",
  () => {
    cy.getProfessorTurmasHistoricasGeral(
      Cypress.env("ANO_LETIVO"),
      "9999999",
    ).as("response");
  },
);

Then("retorna o status 200", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(200);
  });
});

Then("retorna o status 204", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(204);
  });
});

Then("retorna o status 400", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(400);
  });
});

Then("retorna o status 404", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(404);
  });
});

And("o retorno deve conter dados da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
    }
  });
});

And("o retorno deve conter dados de matricula da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter dados da turma considerando inativos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigoComponenteCurricular");
      expect(response.body).to.have.property("codigoAluno");
      expect(response.body).to.have.property("nomeAluno");
      expect(response.body).to.have.property("dataNascimento");
      expect(response.body).to.have.property("nomeSocialAluno");
      expect(response.body).to.have.property("codigoSituacaoMatricula");
      expect(response.body).to.have.property("situacaoMatricula");
      expect(response.body).to.have.property("dataSituacao");
      expect(response.body).to.have.property("dataMatricula");
      expect(response.body).to.have.property("numeroAlunoChamada");
      expect(response.body).to.have.property("celularResponsavel");
      expect(response.body).to.have.property("possuiDeficiencia");
      expect(response.body).to.have.property("transferencia_Interna");
      expect(response.body).to.have.property("remanejado");
      expect(response.body).to.have.property("escolaTransferencia");
      expect(response.body).to.have.property("turmaTransferencia");
      expect(response.body).to.have.property("turmaRemanejamento");
      expect(response.body).to.have.property("parecerConclusivo");
      expect(response.body).to.have.property("nomeResponsavel");
      expect(response.body).to.have.property("tipoResponsavel");
      expect(response.body).to.have.property("dataAtualizacaoContato");
      expect(response.body).to.have.property("codigoMatricula");
      expect(response.body).to.have.property("sequencia");
      expect(response.body).to.have.property("tipoTurma");
      expect(response.body).to.have.property("codigoTurma");
      expect(response.body).to.have.property("codigoEscola");
      expect(response.body).to.have.property("ano");
      expect(response.body).to.have.property("codigoDre");
    }
  });
});

And("o retorno deve conter dados considerando inativos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body[0]).to.have.property("codigoComponenteCurricular");
      expect(response.body[0]).to.have.property("codigoAluno");
      expect(response.body[0]).to.have.property("nomeAluno");
      expect(response.body[0]).to.have.property("dataNascimento");
      expect(response.body[0]).to.have.property("nomeSocialAluno");
      expect(response.body[0]).to.have.property("codigoSituacaoMatricula");
      expect(response.body[0]).to.have.property("situacaoMatricula");
      expect(response.body[0]).to.have.property("dataSituacao");
      expect(response.body[0]).to.have.property("dataMatricula");
      expect(response.body[0]).to.have.property("numeroAlunoChamada");
      expect(response.body[0]).to.have.property("celularResponsavel");
      expect(response.body[0]).to.have.property("possuiDeficiencia");
      expect(response.body[0]).to.have.property("transferencia_Interna");
      expect(response.body[0]).to.have.property("remanejado");
      expect(response.body[0]).to.have.property("escolaTransferencia");
      expect(response.body[0]).to.have.property("turmaTransferencia");
      expect(response.body[0]).to.have.property("turmaRemanejamento");
      expect(response.body[0]).to.have.property("parecerConclusivo");
      expect(response.body[0]).to.have.property("nomeResponsavel");
      expect(response.body[0]).to.have.property("tipoResponsavel");
      expect(response.body[0]).to.have.property("dataAtualizacaoContato");
      expect(response.body[0]).to.have.property("codigoMatricula");
      expect(response.body[0]).to.have.property("sequencia");
      expect(response.body[0]).to.have.property("tipoTurma");
      expect(response.body[0]).to.have.property("codigoTurma");
      expect(response.body[0]).to.have.property("codigoEscola");
      expect(response.body[0]).to.have.property("ano");
      expect(response.body[0]).to.have.property("codigoDre");
    }
  });
});

And("o retorno deve conter lista de turmas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter lista de matriculas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter lista de alunos ativos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter calculo de frequencia", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
    }
  });
});

And("o retorno deve conter dados do redis multplex", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
    }
  });
});

And("o retorno deve conter lista de componentes curriculares do aluno", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter lista de turmas historicas gerais", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve ser uma lista vazia", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array").that.is.empty;
    }
  });
});

// Endpoint GET - /api/turmas/ue/{codigoUe}/sincronizacoes-institucionais/anos-letivos?anosLetivosVigente={anoLetivo}
When(
  "realizo consulta de anos letivos de sincronizações institucionais com UE e ano letivo válidos",
  () => {
    cy.getTurmasSincronizacoesAnosLetivos(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de anos letivos de sincronizações institucionais com UE e ano letivo inválidos",
  () => {
    cy.getTurmasSincronizacoesAnosLetivos(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

And(
  "o retorno deve conter lista de anos letivos de sincronizações institucionais",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.be.an("array");
        if (response.body.length > 0) {
          expect(response.body).not.be.empty;
        }
      }
    });
  },
);

// Endpoint GET - /api/turmas/{codigoTurma}/alunos/anosLetivos/{anoLetivo}
When("realizo consulta de alunos da turma com UE e ano letivo válidos", () => {
  cy.getTurmasAlunosAnoLetivo(
    Cypress.env("TURMA_CODIGO"),
    Cypress.env("ANO_LETIVO"),
  ).as("response");
});

When(
  "realizo consulta de alunos da turma com UE e ano letivo inválidos",
  () => {
    cy.getTurmasAlunosAnoLetivo(
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

// Endpoint GET - /api/ues/{codigoUe}/turmas/{codigoTurma}/sincronizacoes-institucionais
When(
  "realizo consulta de sincronizações institucionais da turma com UE e turma válidos",
  () => {
    cy.getUeTurmaSincronizacoesInstitucionais(
      Cypress.env("UE_CODIGO"),
      Cypress.env("TURMA_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de sincronizações institucionais da turma com UE e turma inválidos",
  () => {
    cy.getUeTurmaSincronizacoesInstitucionais(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And(
  "o retorno deve conter dados de sincronizações institucionais da turma",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.exist;
        expect(response.body).to.not.be.empty;
      }
    });
  },
);

And("o retorno deve conter dados de alunos da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint GET - /api/turmas/{codigoTurma}/sem-redis
When("realizo consulta de turma sem redis com código de turma válido", () => {
  cy.getTurmaSemRedis(Cypress.env("TURMA_CODIGO")).as("response");
});

When("realizo consulta de turma sem redis com código de turma inválido", () => {
  cy.getTurmaSemRedis(Cypress.env("TURMA_CODIGO_INEXISTENTE")).as("response");
});

And("o retorno deve conter dados da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint GET - /api/turmas/itinerario/ensino-medio
When("realizo consulta de itinerário do ensino médio", () => {
  cy.getTurmasItinerarioEnsinoMedio().as("response");
});

And(
  "o retorno deve conter lista de itinerários do ensino médio com id, nome e serie",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.be.an("array");
        expect(response.body).not.be.empty;
        response.body.forEach((item) => {
          expect(item).to.have.property("id");
          expect(item).to.have.property("nome");
          expect(item).to.have.property("serie");
        });
      }
    });
  },
);

// Endpoint GET - /api/turmas/ues/{codigoUe}/modalidades/{modalidade}/anos/{anoLetivo}/componentes?consideraHistorico=false
When(
  "realizo consulta de componentes de turmas por UE, modalidade e ano letivo com dados válidos",
  () => {
    cy.getTurmasComponentes(
      Cypress.env("UE_CODIGO"),
      Cypress.env("MODALIDADE"),
      Cypress.env("ANO_LETIVO"),
      false,
    ).as("response");
  },
);

When(
  "realizo consulta de componentes de turmas por UE, modalidade e ano letivo com dados inválidos",
  () => {
    cy.getTurmasComponentes(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("MODALIDADE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      false,
    ).as("response");
  },
);

And("o retorno deve conter dados de componentes de turmas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
    }
  });
});

// Endpoint GET - /api/turmas/{codigoTurma}/alunos/anosLetivos/{anoLetivo}
When(
  "realizo consulta de alunos da turma por ano letivo com código de turma válido",
  () => {
    cy.getTurmaAlunosPorAnoLetivo(
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de alunos da turma por ano letivo com código de turma inválido",
  () => {
    cy.getTurmaAlunosPorAnoLetivo(
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter dados de alunos da turma por ano letivo", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint GET - /api/turmas/{codigoTurma}/todos-alunos
When(
  "realizo consulta de todos os alunos da turma com código de turma válido",
  () => {
    cy.getTurmaTodosAlunos(Cypress.env("TURMA_CODIGO")).as("response");
  },
);

When(
  "realizo consulta de todos os alunos da turma com código de turma inválido",
  () => {
    cy.getTurmaTodosAlunos(Cypress.env("TURMA_CODIGO_INEXISTENTE")).as(
      "response",
    );
  },
);

And("o retorno deve conter lista de todos os alunos da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint GET - /api/turmas/alunos/{codigoAluno}
When("realizo consulta de turmas do aluno com código de aluno válido", () => {
  cy.getTurmasAluno(Cypress.env("CODIGO_ALUNO")).as("response");
});

When("realizo consulta de turmas do aluno com código de aluno inválido", () => {
  cy.getTurmasAluno(Cypress.env("CODIGO_ALUNO_INEXISTENTE")).as("response");
});

And("o retorno deve conter lista de turmas do aluno", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint GET - /api/turmas/{codigoTurma}/acompanhamento-escolar/todos-alunos
When(
  "realizo consulta de acompanhamento escolar de todos os alunos com código de turma válido",
  () => {
    cy.getTurmaAcompanhamentoEscolarTodosAlunos(Cypress.env("TURMA_CODIGO")).as(
      "response",
    );
  },
);

When(
  "realizo consulta de acompanhamento escolar de todos os alunos com código de turma inválido",
  () => {
    cy.getTurmaAcompanhamentoEscolarTodosAlunos(
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And(
  "o retorno deve conter dados de acompanhamento escolar de todos os alunos",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.exist;
        // expect(response.body).to.not.be.empty;
      }
    });
  },
);

// Endpoint GET - /api/turmas/todos-alunos/ano-turma/{anoTurma}/modalidade/{modalidade}/ano-letivo/{anoLetivo}/dre/{dreCodigo}/inicio/{dataInicio}/fim/{dataFim}
When(
  "realizo consulta de todos os alunos por ano turma, modalidade, ano letivo, DRE e período com dados válidos",
  () => {
    cy.getTurmasTodosAlunosFiltros(
      Cypress.env("TURMA_ANO"),
      Cypress.env("MODALIDADE"),
      Cypress.env("ANO_LETIVO"),
      Cypress.env("DRE_CODIGO"),
      Cypress.env("DATA_INICIO"),
      Cypress.env("DATA_FIM"),
    ).as("response");
  },
);

When(
  "realizo consulta de todos os alunos por ano turma, modalidade, ano letivo, DRE e período com dados inválidos",
  () => {
    cy.getTurmasTodosAlunosFiltros(
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
      Cypress.env("MODALIDADE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
      Cypress.env("DATA_INICIO"),
      Cypress.env("DATA_FIM"),
    ).as("response");
  },
);

And("o retorno deve conter lista de todos os alunos por filtros", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});
