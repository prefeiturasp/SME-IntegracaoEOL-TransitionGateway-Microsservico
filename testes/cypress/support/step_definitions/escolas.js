import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de escolas", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("UE_CODIGO")).to.exist;
});

// THEN
Then("retorna o status {int}", (statusCode) => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(statusCode);
  });
});

// DETALHE DA ESCOLA
When("realizo consulta de detalhe da escola", () => {
  cy.getEscolaDetalhe(true).as("response");
});

When("realizo consulta de detalhe da escola não encontrada", () => {
  cy.getEscolaDetalhe(false).as("response");
});

// DADOS COMPLETOS
When("realizo consulta de dados completos da escola", () => {
  cy.getEscolaDadosCompletos(true).as("response");
});
When("realizo consulta de dados completos da escola não encontrada", () => {
  cy.getEscolaDadosCompletos(false).as("response");
});

// TIPOS DE ESCOLA
When("realizo consulta de tipos de escola", () => {
  cy.getEscolaTipos().as("response");
});

// FUNCIONÁRIOS DA ESCOLA
When("realizo consulta de funcionários da escola", () => {
  cy.getEscolaFuncionarios(true).as("response");
});
When("realizo consulta de funcionários da escola não encontrada", () => {
  cy.getEscolaFuncionarios(false).as("response");
});

// EQUIPAMENTOS
When("realizo consulta de equipamentos das escolas", () => {
  cy.getEscolaEquipamentos().as("response");
});

// UNIDADE EOL
When("realizo consulta de unidade EOL da escola", () => {
  cy.getEscolaUnidadeEol(true).as("response");
});
When("realizo consulta de unidade EOL da escola não encontrada", () => {
  cy.getEscolaUnidadeEol(false).as("response");
});

// SINCRONIZAÇÕES INSTITUCIONAIS
When("realizo consulta de sincronizações institucionais da escola", () => {
  cy.getEscolaSincronizacoesInstitucionais(true).as("response");
});

When(
  "realizo consulta de sincronizações institucionais da escola não encontrada",
  () => {
    cy.getEscolaSincronizacoesInstitucionais(false).as("response");
  },
);

// UNIDADES PARCEIRAS (POST)
When("realizo requisição de unidades parceiras", () => {
  cy.postEscolasUnidadesParceiras(true).as("response");
});

When("realizo requisição de unidades parceiras inválida", () => {
  cy.postEscolasUnidadesParceiras(false).as("response");
});

// TODAS UNIDADES
When("realizo consulta de todas as unidades", () => {
  cy.getEscolaTodasUnidades().as("response");
});

// TIPOS UNIDADE EDUCAÇÃO
When("realizo consulta de tipos de unidade de educação", () => {
  cy.getTiposUnidadeEducacao().as("response");
});

// AND
And("o retorno deve conter dados da escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body[0]).to.have.property("codigoEscola");
      expect(response.body[0]).to.have.property("nomeEscola");
      expect(response.body[0]).to.have.property("nomeDRE");
      expect(response.body[0].codigoEscola).to.not.be.empty;
      expect(response.body[0].nomeEscola).to.not.be.empty;
      expect(response.body[0]).to.have.property("siglaDRE");
      expect(response.body[0]).to.have.property("tipoEscola");
      expect(response.body[0]).to.have.property("siglaTipoEscola");
    }
  });
});

And("o retorno deve conter dados da unidade pelo código EOL", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigo");
      expect(response.body).to.have.property("sigla");
      expect(response.body).to.have.property("nomeUnidade");
      expect(response.body).to.have.property("tipo");
      expect(response.body).to.have.property("codigoReferencia");
      expect(response.body.codigo).to.not.be.empty;
      expect(response.body.sigla).to.not.be.empty;
    }
  });
});

And("o retorno deve conter dados completos da escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigo");
      expect(response.body).to.have.property("nome");
      expect(response.body).to.have.property("nomeDRE");
      expect(response.body).to.have.property("siglaDRE");
      expect(response.body.codigo).to.not.be.empty;
    }
  });
});
And("o retorno deve conter lista de tipos de escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigo");
        expect(response.body[0]).to.have.property("descricaoSigla");
      }
    }
  });
});

And("o retorno deve conter lista de tipos de unidades educacionais", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).to.be.an("array");
        expect(response.body).not.be.empty;
      }
    }
  });
});

And("o retorno deve conter lista de funcionários da escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoRF");
        expect(response.body[0]).to.have.property("nomeServidor");
      }
    }
  });
});

And("o retorno deve ser uma lista vazia", () => {
  cy.get("@response").then((response) => {
    expect(response.body).to.be.an("array").that.is.empty;
  });
});

And("o retorno deve conter lista de equipamentos das escolas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("cd_equipamento");
        expect(response.body[0]).to.have.property("nm_exibicao_equipamento");
      }
    }
  });
});

And("o retorno deve conter lista de sincronizações institucionais", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("ueCodigo");
      expect(response.body).to.have.property("dataAtualizacao");
      expect(response.body).to.have.property("dreCodigo");
      expect(response.body).to.have.property("ueNome");
      expect(response.body).to.have.property("tipoEscolaCodigo");
    }
  });
});

And("o retorno deve conter lista de unidades parceiras", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

And("o retorno deve conter lista de unidades", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
    }
  });
});

When("realizo consulta de escola pelo código UE válido", () => {
  cy.postEscolas(true).as("response");
});

When("realizo consulta de escola pelo código UE inexistente", () => {
  cy.postEscolas(false).as("response");
});

When("realizo consulta de subprefeituras pelo código UE válido", () => {
  cy.getEscolaSubprefeituras(Cypress.env("UE_CODIGO")).as("response");
});

When("realizo consulta de subprefeituras pelo código UE inexistente", () => {
  cy.getEscolaSubprefeituras(Cypress.env("UE_CODIGO_INEXISTENTE")).as(
    "response",
  );
});

And("o retorno deve conter dados de uma escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigoEscola");
      expect(response.body).to.have.property("nomeEscola");
      expect(response.body).to.have.property("nomeDRE");
      expect(response.body).to.have.property("siglaDRE");
      expect(response.body).to.have.property("codigoDRE");
      expect(response.body).to.have.property("tipoEscola");
      expect(response.body).to.have.property("siglaTipoEscola");
      expect(response.body).to.have.property("codigoTipoEscola");
    }
  });
});

And("o retorno deve conter dados de subprefeituras", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint 3 - /api/escolas/{codigoUe}/funcionarios/cargos/{codigoCargo}/
When(
  "realizo consulta de funcionários por cargo com código UE e código cargo válidos",
  () => {
    cy.getFuncionariosPorCargo(
      Cypress.env("UE_CODIGO_FUNCIONARIOS"),
      Cypress.env("CARGO_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por cargo com código UE e código cargo inválidos",
  () => {
    cy.getFuncionariosPorCargo(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("CARGO_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de funcionários por cargo", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint 4 - /api/escolas/{codigoUe}/funcionarios/cargos/?cargos={codigoCargo}&codigo_dre={codigoDre}
When(
  "realizo consulta de funcionários por cargos com código UE e código DRE válidos",
  () => {
    cy.getFuncionariosPorCargos(
      Cypress.env("UE_CODIGO_FUNCIONARIOS"),
      Cypress.env("CARGO_CODIGO"),
      Cypress.env("DRE_CODIGO_FUNCIONARIOS"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por cargos com código UE e código DRE inválidos",
  () => {
    cy.getFuncionariosPorCargos(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("CARGO_CODIGO_INEXISTENTE"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de funcionários por cargos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint 5 - /api/escolas/{codigoUe}/funcionarios/funcoes-atividades/?funcoes_atividades={codigo}&codigo_dre={codigoDre}
When(
  "realizo consulta de funcionários por funções atividades com código UE e código DRE válidos",
  () => {
    cy.getFuncionariosPorFuncoesAtividades(
      Cypress.env("UE_CODIGO_FUNCIONARIOS"),
      Cypress.env("FUNCAO_ATIVIDADE_CODIGO"),
      Cypress.env("DRE_CODIGO_FUNCIONARIOS"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por funções atividades com código UE e código DRE inválidos",
  () => {
    cy.getFuncionariosPorFuncoesAtividades(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("FUNCAO_ATIVIDADE_CODIGO_INEXISTENTE"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And(
  "o retorno deve conter lista de funcionários por funções atividades",
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

// Endpoint 6 - /api/escolas/{codigoUe}/funcionarios/funcoes-atividades/{codigoFuncaoAtividade}/
When(
  "realizo consulta de funcionários por função atividade com código UE e código função atividade válidos",
  () => {
    cy.getFuncionariosPorFuncaoAtividade(
      Cypress.env("UE_CODIGO"),
      Cypress.env("FUNCAO_ATIVIDADE_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por função atividade com código UE e código função atividade inválidos",
  () => {
    cy.getFuncionariosPorFuncaoAtividade(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("FUNCAO_ATIVIDADE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de funcionários por função atividade", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint 7 - /api/escolas/{codigoUe}/funcionarios/funcoes-externas/?funcoes={codigo}&codigo_dre={codigoDre}
When(
  "realizo consulta de funcionários por funções externas com código UE, código função externa e código DRE válidos",
  () => {
    cy.getFuncionariosPorFuncoesExternas(
      Cypress.env("UE_CODIGO_FUNCIONARIOS"),
      Cypress.env("FUNCAO_EXTERNA_CODIGO"),
      Cypress.env("DRE_CODIGO_FUNCOES_EXTERNAS"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por funções externas com código UE, código função externa e código DRE inválidos",
  () => {
    cy.getFuncionariosPorFuncoesExternas(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("FUNCAO_EXTERNA_CODIGO_INEXISTENTE"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de funcionários por funções externas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint 8 - /api/escolas/{codigoUe}/funcionarios/funcoes-externas/{codigoFuncaoExterna}/
When(
  "realizo consulta de funcionários por função externa com código UE e código função externa válidos",
  () => {
    cy.getFuncionariosPorFuncaoExterna(
      Cypress.env("UE_CODIGO"),
      Cypress.env("FUNCAO_EXTERNA_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de funcionários por função externa com código UE e código função externa inválidos",
  () => {
    cy.getFuncionariosPorFuncaoExterna(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("FUNCAO_EXTERNA_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de funcionários por função externa", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint 9 - /api/matriculas/escolas/{codigoUe}/quantidades
When(
  "realizo consulta de quantidade de matrículas pelo código UE válido",
  () => {
    cy.getMatriculasEscolaQuantidades(Cypress.env("UE_CODIGO")).as("response");
  },
);

When(
  "realizo consulta de quantidade de matrículas pelo código UE inválido",
  () => {
    cy.getMatriculasEscolaQuantidades(Cypress.env("UE_CODIGO_INEXISTENTE")).as(
      "response",
    );
  },
);

And("o retorno deve conter dados de quantidade de matrículas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint 10 - /api/matriculas/escolas/dre/{dreCodigo}/quantidades
When(
  "realizo consulta de quantidade de matrículas pelo código DRE válido",
  () => {
    cy.getMatriculasEscolaDreQuantidades(Cypress.env("DRE_CODIGO")).as(
      "response",
    );
  },
);

When(
  "realizo consulta de quantidade de matrículas pelo código DRE inválido",
  () => {
    cy.getMatriculasEscolaDreQuantidades(
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter dados de quantidade de matrículas por DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint 11 - /api/escolas/{codigoUe}/alunos/quantidade/
When("realizo consulta de quantidade de alunos pelo código UE válido", () => {
  cy.getEscolaAlunosQuantidade(Cypress.env("UE_CODIGO")).as("response");
});

When("realizo consulta de quantidade de alunos pelo código UE inválido", () => {
  cy.getEscolaAlunosQuantidade(Cypress.env("UE_CODIGO_INEXISTENTE")).as(
    "response",
  );
});

And("o retorno deve conter dados de quantidade de alunos", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint 12 - /api/escolas/{codigoUe}/alunos/{codigoAluno}/matriculas/
When(
  "realizo consulta de matrículas do aluno pelo código UE e código aluno válidos",
  () => {
    cy.getEscolaAlunoMatriculas(
      Cypress.env("UE_CODIGO_MATRICULA"),
      Cypress.env("CODIGO_ALUNO_MATRICULA"),
    ).as("response");
  },
);

When(
  "realizo consulta de matrículas do aluno pelo código UE e código aluno inválidos",
  () => {
    cy.getEscolaAlunoMatriculas(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("CODIGO_ALUNO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de matrículas do aluno", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoAluno");
        expect(response.body[0]).to.have.property("nomeAluno");
        expect(response.body[0]).to.have.property("nomeSocialAluno");
        expect(response.body[0]).to.have.property("codigoSituacaoMatricula");
        expect(response.body[0]).to.have.property("situacaoMatricula");
        expect(response.body[0]).to.have.property("dataSituacao");
        expect(response.body[0]).to.have.property("codigoTurma");
        expect(response.body[0]).to.have.property("codigoMatricula");
        expect(response.body[0]).to.have.property("anoLetivo");
      }
    }
  });
});

// Endpoint - /api/escolas/modalidades_ensino
When("realizo consulta de modalidades de ensino", () => {
  cy.getModalidadesEnsino().as("response");
});

And("o retorno deve conter lista de modalidades de ensino", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      expect(response.body).not.be.empty;
    }
  });
});

// Endpoint - /api/escolas/{codigoUE}/salas/{tipoSala}/anos_letivos/{anoLetivo}
When(
  "realizo consulta de salas pelo código UE, tipo de sala e ano letivo válidos",
  () => {
    cy.getEscolaSalas(
      Cypress.env("UE_CODIGO"),
      Cypress.env("TIPO_SALA"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de salas pelo código UE, tipo de sala e ano letivo inválidos",
  () => {
    cy.getEscolaSalas(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("TIPO_SALA_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter dados de salas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint - /api/escolas/{codigoUE}/turmas/anos_letivos/{anoLetivo}
When("realizo consulta de turmas pelo código UE e ano letivo válidos", () => {
  cy.getEscolaTurmas(Cypress.env("UE_CODIGO"), Cypress.env("ANO_LETIVO")).as(
    "response",
  );
});

When("realizo consulta de turmas pelo código UE e ano letivo inválidos", () => {
  cy.getEscolaTurmas(
    Cypress.env("UE_CODIGO_INEXISTENTE"),
    Cypress.env("ANO_LETIVO_INEXISTENTE"),
  ).as("response");
});

And("o retorno deve conter lista de turmas", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint - /api/escolas/{codigoUE}/turmasSondagem/anos_letivos/{anoLetivo}
When(
  "realizo consulta de turmas de sondagem pelo código UE e ano letivo válidos",
  () => {
    cy.getEscolaTurmasSondagem(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de turmas de sondagem pelo código UE e ano letivo inválidos",
  () => {
    cy.getEscolaTurmasSondagem(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de turmas de sondagem", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

And("a mensagem deve ser {string}", (mensagem) => {
  cy.get("@response").then((response) => {
    expect(JSON.stringify(response.body)).contain(mensagem);
  });
});

When(
  "realizo consulta de professores pelo código UE e ano letivo válidos",
  () => {
    cy.getEscolaProfessores(
      Cypress.env("UE_CODIGO"),
      Cypress.env("ANO_LETIVO"),
    ).as("response");
  },
);

When(
  "realizo consulta de professores pelo código UE e ano letivo inválidos",
  () => {
    cy.getEscolaProfessores(
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de professores", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
        expect(response.body[0]).to.have.property("codigoRF");
        expect(response.body[0]).to.have.property("nome");
        expect(response.body[0]).to.have.property("cargo");
        expect(response.body[0]).to.have.property("cpf");
        expect(response.body[0]).to.have.property("dataInicioExercicio");
      }
    }
  });
});
