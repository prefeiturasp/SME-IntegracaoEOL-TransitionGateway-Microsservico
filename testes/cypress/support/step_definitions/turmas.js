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
