import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de alunos", () => {
  expect(Cypress.env("API_URL")).to.exist;
});

When("realizo consulta de informações do aluno", () => {
  cy.getAlunoInformacoes(true).as("response");
});

When("realizo consulta de informações do aluno não encontrado", () => {
  cy.getAlunoInformacoes(false).as("response");
});

When("realizo consulta de necessidades especiais do aluno", () => {
  cy.getAlunoNecessidadesEspeciais().as("response");
});

When("realizo consulta de turmas do aluno", () => {
  cy.getAlunoTurmas().as("response");
});

When("realizo consulta de lista de alunos por códigos", () => {
  cy.getAlunosPorCodigos().as("response");
});

When("realizo consulta de alunos PAP do ano corrente", () => {
  cy.getAlunosPapAnoCorrente().as("response");
});

When("realizo consulta de alunos PAP por ano letivo", () => {
  cy.getAlunosPapPorAnoLetivo().as("response");
});

When("realizo consulta de turmas PAP por ano letivo e escola", () => {
  cy.getTurmasPapPorAnoLetivoEEscola().as("response");
});

When("realizo consulta de componentes das turmas de programa do aluno", () => {
  cy.getComponentesTurmasProgramaAluno().as("response");
});

When("realizo consulta de verificação de alunos em turmas PAP", () => {
  cy.getVerificacaoAlunosTurmasPap().as("response");
});

When("realizo consulta de dados SRM PAEE do aluno", () => {
  cy.getAlunoSrmPaee(true).as("response");
});

When("realizo consulta de dados SRM PAEE do aluno não encontrado", () => {
  cy.getAlunoSrmPaee(false).as("response");
});

When("realizo consulta de turmas do aluno por código", () => {
  cy.getAlunoTurmas().as("response");
});

// THEN
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

// AND

And("o retorno deve conter dados de SRM PAEE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("codigoEscola");
        expect(response.body[0]).to.have.property("codigoAluno");
      }
    }
  });
});

And("o retorno deve conter informações do aluno", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigoAluno");
      expect(response.body).to.have.property("nomeAluno");
      expect(response.body).to.have.property("nomeMae");
      expect(response.body).to.have.property("sexo");
      expect(response.body).to.have.property("grupoEtnico");
      expect(response.body).to.have.property("nacionalidade");
      expect(response.body).to.have.property("endereco");
      expect(response.body).to.have.property("ehImigrante");
      expect(response.body).to.have.property("nis");
      expect(response.body).to.have.property("cns");
    }
  });
});

And("o retorno deve conter informações das necessidades especiais", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigoAluno");
      expect(response.body).to.have.property("tipoNecessidadeEspecial");
      expect(response.body).to.have.property("descricaoNecessidadeEspecial");
      expect(response.body).to.have.property("tipoRecurso");
      expect(response.body).to.have.property("descricaoRecurso");
    }
  });
});

And("o retorno deve conter informações das turmas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("anoLetivo");
        expect(response.body[0]).to.have.property("nomeAluno");
        expect(response.body[0]).to.have.property("nomeSocialAluno");
        expect(response.body[0]).to.have.property("codigoSituacaoMatricula");
        expect(response.body[0]).to.have.property("situacaoMatricula");
        expect(response.body[0]).to.have.property("dataSituacao");
        expect(response.body[0]).to.have.property("dataNascimento");
        expect(response.body[0]).to.have.property("idade");
        expect(response.body[0]).to.have.property("documentoCpf");
        expect(response.body[0]).to.have.property("dataMatricula");
        expect(response.body[0]).to.have.property("numeroAlunoChamada");
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("nomeResponsavel");
        expect(response.body[0]).to.have.property("tipoResponsavel");
        expect(response.body[0]).to.have.property("celularResponsavel");
        expect(response.body[0]).to.have.property("dataAtualizacaoContato");
        expect(response.body[0]).to.have.property("codigoEscola");
        expect(response.body[0]).to.have.property("codigoTipoTurma");
        expect(response.body[0]).to.have.property("dataAtualizacaoTabela");
      }
    }
  });
});

And("o retorno deve conter informações dos alunos por códigos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoAluno");
        expect(response.body[0]).to.have.property("tipoTurno");
        expect(response.body[0]).to.have.property("anoLetivo");
        expect(response.body[0]).to.have.property("nomeAluno");
        expect(response.body[0]).to.have.property("nomeSocialAluno");
        expect(response.body[0]).to.have.property("codigoSituacaoMatricula");
        expect(response.body[0]).to.have.property("situacaoMatricula");
        expect(response.body[0]).to.have.property("dataSituacao");
        expect(response.body[0]).to.have.property("dataNascimento");
        expect(response.body[0]).to.have.property("numeroAlunoChamada");
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("nomeResponsavel");
        expect(response.body[0]).to.have.property("tipoResponsavel");
        expect(response.body[0]).to.have.property("celularResponsavel");
        expect(response.body[0]).to.have.property("dataAtualizacaoContato");
        expect(response.body[0]).to.have.property("codigoTipoTurma");
        expect(response.body[0]).to.have.property("turmaNome");
        expect(response.body[0]).to.have.property("etapaEnsino");
        expect(response.body[0]).to.have.property("cicloEnsino");
        expect(response.body[0]).to.have.property("descEtapaEnsino");
        expect(response.body[0]).to.have.property("descCicloEnsino");
        expect(response.body[0]).to.have.property("dataAtualizacaoTabela");
      }
    }
  });
});

And("o retorno deve conter informações dos alunos PAP por ano letivo", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoAluno");
        expect(response.body[0]).to.have.property("nome");
        expect(response.body[0]).to.have.property("anoLetivo");
      }
    }
  });
});

And("o retorno deve ser vazio", () => {
  cy.get("@response").then((response) => {
    expect(response.body).to.be.empty;
  });
});

And("o retorno deve conter lista de turmas PAP", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("turmaNome");
      }
    }
  });
});

And("o retorno deve conter componentes das turmas de programa", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoAluno");
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("codigoComponenteCurricular");
      }
    }
  });
});

And("o retorno deve conter informações das turmas do aluno", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("anoLetivo");
      }
    }
  });
});
