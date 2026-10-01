import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ========================================
// ACESSO API
// ========================================

Given("que possuo acesso à API de professores", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("REGISTRO_FUNCIONAL")).to.exist;
});

// ========================================
// PROFESSOR VÁLIDO
// ========================================

When("realizo consulta de validade do professor", () => {
  cy.getProfessorValidade(true).as("response");
});

When("realizo consulta de validade do professor não válido", () => {
  cy.getProfessorValidade(false).as("response");
});

// ========================================
// PROFESSOR POR RF
// ========================================

When("realizo consulta de professor por RF", () => {
  cy.getProfessorPorRF(true).as("response");
});

When("realizo consulta de professor por RF com RF inválido", () => {
  cy.getProfessorPorRF(false).as("response");
});

// THEN
Then("retorna o status {int}", (statusCode) => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(statusCode);
  });
});

// AND
And("o retorno deve ser um RF EMEI verdadeiro", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.true;
    }
  });
});

And("o retorno deve ser falso", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.false;
    }
  });
});

And("o retorno deve conter nome e cpf", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("nome");
      expect(response.body).to.have.property("cpf");
      expect(response.body.nome).to.not.be.empty;
      expect(response.body.cpf).to.not.be.empty;
    }
  });
});

And("o retorno deve conter o nome do professor", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.be.a("string");
    }
  });
});

// Endpoint GET - /api/professores/{anoLetivo}/AutoComplete/{dreCodigo}/?ue_id={ueCodigo}&nome={nome}
When(
  "realizo consulta de autocomplete de professores com DRE, UE e nome válidos",
  () => {
    cy.getProfessoresAutoComplete(
      Cypress.env("ANO_LETIVO"),
      Cypress.env("DRE_CODIGO"),
      Cypress.env("UE_CODIGO"),
      Cypress.env("NOME_ALUNO"),
    ).as("response");
  },
);

When(
  "realizo consulta de autocomplete de professores com DRE, UE e nome inválidos",
  () => {
    cy.getProfessoresAutoComplete(
      Cypress.env("ANO_LETIVO"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
      Cypress.env("UE_CODIGO_INEXISTENTE"),
      Cypress.env("NOME_ALUNO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter lista de professores no autocomplete", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint POST - /api/professores/{anoLetivo}/BuscarPorListaRF/
When(
  "realizo envio de busca de professores por lista de RF com ano letivo e registro funcional válidos",
  () => {
    cy.postProfessoresBuscarPorListaRF(Cypress.env("ANO_LETIVO"), true).as(
      "response",
    );
  },
);

When(
  "realizo envio de busca de professores por lista de RF com ano letivo e registro funcional inválidos",
  () => {
    cy.postProfessoresBuscarPorListaRF(
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      false,
    ).as("response");
  },
);

And("o retorno deve conter lista de professores por RF", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

// Endpoint GET - /api/professores/{registroFuncional}/BuscarPorRf/{anoLetivo}/
When("realizo consulta de professor por RF e ano letivo válidos", () => {
  cy.getProfessorBuscarPorRF(
    Cypress.env("REGISTRO_FUNCIONAL"),
    Cypress.env("ANO_LETIVO"),
  ).as("response");
});

When("realizo consulta de professor por RF e ano letivo inválidos", () => {
  cy.getProfessorBuscarPorRF(
    Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE"),
    Cypress.env("ANO_LETIVO"),
  ).as("response");
});

And("o retorno deve conter dados do professor por RF", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint GET - /api/professores/{registroFuncional}/BuscarPorRfDreUe/{anoLetivo}/?dre_id={dreCodigo}&ue_id={ueCodigo}
When(
  "realizo consulta de professor por RF, ano letivo, DRE e UE válidos",
  () => {
    cy.getProfessorBuscarPorRFDreUe(
      Cypress.env("REGISTRO_FUNCIONAL"),
      Cypress.env("ANO_LETIVO"),
      Cypress.env("DRE_CODIGO"),
      Cypress.env("UE_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de professor por RF, ano letivo, DRE e UE inválidos",
  () => {
    cy.getProfessorBuscarPorRFDreUe(
      Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE"),
      Cypress.env("ANO_LETIVO"),
      Cypress.env("DRE_CODIGO_INEXISTENTE"),
      Cypress.env("UE_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter dados do professor por RF, DRE e UE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

// Endpoint POST - /api/professores/{registroFuncional}/disciplina/{disciplinaId}/turmas/
When(
  "realizo envio de turmas de professor por disciplina com registro funcional, disciplina e turma válidos",
  () => {
    cy.postProfessorTurmasPorDisciplina(
      Cypress.env("REGISTRO_FUNCIONAL"),
      Cypress.env("DISCIPLINA_ID"),
      true,
    ).as("response");
  },
);

When(
  "realizo envio de turmas de professor por disciplina com registro funcional, disciplina e turma inválidos",
  () => {
    cy.postProfessorTurmasPorDisciplina(
      Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE"),
      Cypress.env("DISCIPLINA_ID_INEXISTENTE"),
      false,
    ).as("response");
  },
);

And("o retorno deve conter lista de turmas do professor por disciplina", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

When(
  "realizo consulta de EMEI do professor com registro funcional válido",
  () => {
    cy.getProfessorEhEmei(true).as("response");
  },
);

When(
  "realizo consulta de EMEI do professor com registro funcional inválido",
  () => {
    cy.getProfessorEhEmei(false).as("response");
  },
);

When(
  "realizo consulta de turmas do professor com registro funcional válido",
  () => {
    cy.getProfessorTurmas(true).as("response");
  },
);

When(
  "realizo consulta de turmas do professor com registro funcional inválido",
  () => {
    cy.getProfessorTurmas(false).as("response");
  },
);

When(
  "realizo consulta de turmas do professor por ano letivo com registro funcional válido",
  () => {
    cy.getProfessorTurmasPorAnoLetivo(Cypress.env("ANO_LETIVO"), true).as(
      "response",
    );
  },
);

When(
  "realizo consulta de turmas do professor por ano letivo com registro funcional inválido",
  () => {
    cy.getProfessorTurmasPorAnoLetivo(
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      false,
    ).as("response");
  },
);

When(
  "realizo consulta de turmas atribuídas pelo professor na escola com dados válidos",
  () => {
    cy.getProfessorTurmasNaEscola(Cypress.env("ANO_LETIVO"), true).as(
      "response",
    );
  },
);

When(
  "realizo consulta de turmas atribuídas pelo professor na escola com dados inválidos",
  () => {
    cy.getProfessorTurmasNaEscola(
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      false,
    ).as("response");
  },
);

When(
  "realizo consulta de turmas de professores por escola e ano letivo válidos",
  () => {
    cy.getTurmasProfessoresNaEscola(Cypress.env("ANO_LETIVO"), true).as(
      "response",
    );
  },
);

When(
  "realizo consulta de turmas de professores por escola e ano letivo inválidos",
  () => {
    cy.getTurmasProfessoresNaEscola(
      Cypress.env("ANO_LETIVO_INEXISTENTE"),
      false,
    ).as("response");
  },
);

When("realizo consulta de atribuição do professor em data válida", () => {
  cy.getProfessorAtribuicaoPorData(
    Cypress.env("REGISTRO_FUNCIONAL"),
    Cypress.env("TURMA_CODIGO"),
    "2026-10-31",
    true,
  ).as("response");
});

When("realizo consulta de atribuição do professor em data inválida", () => {
  cy.getProfessorAtribuicaoPorData(
    Cypress.env("REGISTRO_FUNCIONAL"),
    Cypress.env("TURMA_CODIGO"),
    "2026-10-31",
    false,
  ).as("response");
});

When("realizo consulta de status da atribuição do professor em turma", () => {
  cy.getProfessorStatusAtribuicao(
    Cypress.env("REGISTRO_FUNCIONAL"),
    Cypress.env("TURMA_CODIGO"),
  ).as("response");
});

When(
  "realizo consulta de atribuição do professor em turma e disciplina com data válida",
  () => {
    cy.getProfessorVerificarAtribuicaoDisciplina(
      Cypress.env("REGISTRO_FUNCIONAL"),
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("DISCIPLINA_ID"),
      "2026-10-31",
    ).as("response");
  },
);

When(
  "realizo consulta de atribuições de professor em turma e disciplina no formato ISO",
  () => {
    cy.getAtribuicoesTurmaDisciplinaDataIso(
      Cypress.env("TURMA_CODIGO"),
      Cypress.env("DISCIPLINA_ID"),
      "2026-10-31",
    ).as("response");
  },
);

And("o retorno deve conter lista de turmas do professor", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

And(
  "o retorno deve conter lista de turmas atribuídas ao professor na escola",
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

And("o retorno deve conter lista de turmas por escola e ano letivo", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
});

And("o retorno deve conter status da atribuição do professor", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});

And(
  "o retorno deve conter lista de atribuições de turma e disciplina em data ISO",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.be.an("array");
      }
    });
  },
);

And(
  "a mensagem de erro deve ser Não foram encontradas turmas atribuídas.",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 404) {
        expect(response.body).to.eq("Não foram encontradas turmas atribuídas.");
      }
    });
  },
);
