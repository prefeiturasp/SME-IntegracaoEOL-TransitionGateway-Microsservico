import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de alunos", () => {
  expect(Cypress.env("API_URL")).to.exist;
});

// THEN
Then("retorna o status {int}", (statusCode) => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(statusCode);
  });
});

// WHEN
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

When(
  "realizo consulta de quantidade de alunos matriculados no ano letivo {int}",
  (ano) => {
    cy.getAlunosMatriculadosQuantidade(ano).as("response");
  },
);

When(
  "realizo consulta de alunos matriculados no ano letivo {int} filtrando por componente curricular",
  (ano) => {
    cy.getAlunosMatriculados(ano, Cypress.env("COMPONENTE_CURRICULAR")).as(
      "response",
    );
  },
);

When(
  "realizo consulta de alunos no ano letivo {int} pelo código do aluno",
  (ano) => {
    cy.getAlunosPorCodigo(ano, Cypress.env("CODIGO_ALUNO")).as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar sem informar filtros",
  () => {
    cy.getDadosAcompanhamentoEscolar().as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar pelo código do aluno",
  () => {
    cy.getDadosAcompanhamentoEscolar(
      `?codigo_aluno=${Cypress.env("CODIGO_ALUNO")}`,
    ).as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar pelo código do aluno inexistente",
  () => {
    cy.getDadosAcompanhamentoEscolar(`?codigo_aluno=9999999`).as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar pelo código da DRE",
  () => {
    cy.getDadosAcompanhamentoEscolar(
      `?codigo_dre=${Cypress.env("DRE_CODIGO")}&codigo_aluno=6376605`,
    ).as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar pelo código da UE",
  () => {
    cy.getDadosAcompanhamentoEscolar(
      `?codigo_ue=${Cypress.env("UE_CODIGO")}`,
    ).as("response");
  },
);

When(
  "realizo consulta de dados de acompanhamento escolar pelo CPF do responsável",
  () => {
    cy.getDadosAcompanhamentoEscolar(
      `?cpf_responsavel=${Cypress.env("CPF_RESPONSAVEL")}`,
    ).as("response");
  },
);

When("realizo consulta de responsáveis pelo código da UE", () => {
  cy.getResponsaveis(`?codigo_ue=${Cypress.env("UE_CODIGO")}`).as("response");
});

When("realizo consulta de responsáveis pelo código da UE inexistente", () => {
  cy.getResponsaveis(`?codigo_ue=9999999`).as("response");
});

When("realizo consulta de responsáveis pelo código da DRE", () => {
  cy.getResponsaveis(
    `?codigo_dre=${Cypress.env("DRE_CODIGO")}&codigo_ue=000191`,
  ).as("response");
});

When("realizo consulta de responsáveis pelo código da DRE inexistente", () => {
  cy.getResponsaveis(`?codigo_dre=9999999`).as("response");
});

When("realizo consulta de responsável resumido com CPF não encontrado", () => {
  cy.getResponsavelResumido("111111111111").as("response");
});

When("realizo consulta de responsável resumido com CPF válido", () => {
  cy.getResponsavelResumido(Cypress.env("CPF_RESPONSAVEL")).as("response");
});

When("realizo consulta de responsável resumido com CPF inválido", () => {
  cy.getResponsavelResumido("abc").as("response");
});

When("realizo consulta de alunos ativos da turma", () => {
  cy.getAlunosAtivosTurma(Cypress.env("TURMA_CODIGO")).as("response");
});

When(
  "realizo consulta de alunos ativos da turma pelo código da turma inexistente",
  () => {
    cy.getAlunosAtivosTurma(Cypress.env("TURMA_CODIGO_INEXISTENTE")).as(
      "response",
    );
  },
);

When(
  "realizo consulta de alunos ativos da turma até a data de referência",
  () => {
    cy.getAlunosAtivosTurmaPorData(
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("DATA_REFERENCIA_FIM"),
    ).as("response");
  },
);

When(
  "realizo consulta de alunos ativos da turma até a data de referência pelo código da turma inexistente",
  () => {
    cy.getAlunosAtivosTurmaPorData(
      Cypress.env("TURMA_CODIGO_INEXISTENTE"),
      Cypress.env("DATA_REFERENCIA_FIM"),
    ).as("response");
  },
);

When(
  "realizo consulta de alunos ativos da turma com data de referência fim inválida",
  () => {
    cy.getAlunosAtivosTurmaPorData(
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("DATA_REFERENCIA_FIM_INVALIDA"),
    ).as("response");
  },
);

When(
  "realizo consulta de turmas do aluno por código da UE e ano letivo válidos",
  () => {
    cy.getTurmasAlunoPorUeAnoLetivo(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de turmas do aluno por código da UE, ano letivo válidos e nome do aluno",
  () => {
    cy.getTurmasAlunoPorUeAnoLetivo(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
      Cypress.env("NOME_ALUNO"),
    ).as("response");
  },
);

When("realizo consulta de turmas do aluno com código de UE inexistente", () => {
  cy.getTurmasAlunoPorUeAnoLetivo(
    Cypress.env("UE_CODIGO_INEXISTENTE"),
    Cypress.env("ANO_LETIVO"),
  ).as("response");
});

When("realizo consulta de turmas do aluno com ano letivo inexistente", () => {
  cy.getTurmasAlunoPorUeAnoLetivo(
    Cypress.env("UE_CODIGO"),
    Cypress.env("ANO_LETIVO_INEXISTENTE"),
  ).as("response");
});

When(
  "realizo consulta de turmas do aluno com nome de aluno inexistente",
  () => {
    cy.getTurmasAlunoPorUeAnoLetivo(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
      Cypress.env("NOME_ALUNO_INEXISTENTE"),
    ).as("response");
  },
);

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

And("o retorno deve conter a quantidade de alunos matriculados", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
    }
  });
});

And("o retorno deve conter lista de alunos matriculados", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      // expect(response.body).not.be.empty;
    }
  });
});

And("o retorno deve conter lista de alunos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      expect(response.body).not.be.empty;
    }
  });
});

And("o retorno deve conter lista de dados de acompanhamento escolar", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      expect(response.body).not.be.empty;
    }
  });
});

And("o retorno deve conter lista de responsáveis", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      expect(response.body).not.be.empty;
    }
  });
});

And("o retorno deve ser uma lista vazia", () => {
  cy.get("@response").then((response) => {
    expect(response.body).to.be.empty;
  });
});

And("o retorno deve conter os dados do responsável", () => {
  cy.get("@response").then((response) => {
    expect(response.body).to.exist;
    expect(response.body).to.not.be.empty;
  });
});

And("a mensagem de retorno deve ser {string}", (mensagem) => {
  cy.get("@response").then((response) => {
    // expect(JSON.stringify(response.body)).contain(mensagem);
    expect(JSON.stringify(response.body)).contain(mensagem);
  });
});

And("o retorno deve conter lista de alunos ativos da turma", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
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
