import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ========================================
// ACESSO API
// ========================================

Given("que possuo acesso à API de funcionários", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
});

// ========================================
// NOME SERVIDOR
// ========================================

When("realizo consulta de nome do servidor", () => {
  cy.getNomeServidor(true).as("response");
});

When("realizo consulta de nome do servidor não encontrado", () => {
  cy.getNomeServidor(false).as("response");
});

When("realizo consulta de nome do funcionário no EOL", () => {
  cy.getFuncionarioNomeEol(true).as("response");
});

When("realizo consulta de nome do funcionário no EOL não encontrado", () => {
  cy.getFuncionarioNomeEol(false).as("response");
});

When("realizo consulta de funcionários por RFs", () => {
  cy.postBuscarPorListaRf(true).as("response");
});

When("realizo consulta de funcionários por RFs com RFs inválidos", () => {
  cy.postBuscarPorListaRf(false).as("response");
});

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

And("o retorno deve ser verdadeiro", () => {
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

And("o retorno deve conter o nome do funcionário", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.be.a("string");
    }
  });
});

And("o retorno deve conter os RFs dos funcionários", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.be.an("array");
      expect(response.body.length).to.be.greaterThan(0);
    }
  });
});

const listaCheck = () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).not.be.empty;
      }
    }
  });
};

const dadosCheck = () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
};

Given("que possuo acesso à API de funcionários", () => {
  cy.log(
    "Acesso à API de funcionários garantido via API_KEY configurada no ambiente",
  );
});

// GET /api/funcionarios/DadosSigpae/{codigo_rf}
When("realizo consulta de dados Sigpae do funcionário com RF válido", () => {
  cy.getFuncionarioDadosSigpae(Cypress.env("REGISTRO_FUNCIONAL")).as(
    "response",
  );
});

When(
  "realizo consulta de dados Sigpae do funcionário com RF inexistente",
  () => {
    cy.getFuncionarioDadosSigpae(
      Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE"),
    ).as("response");
  },
);

And("o retorno deve conter dados Sigpae do funcionário", dadosCheck);

// GET /api/funcionarios/atribuicao/{registro_funcional}/cargo/{codigo_cargo}
When(
  "realizo consulta de atribuição do funcionário por cargo com RF e código do cargo válidos",
  () => {
    cy.getFuncionarioAtribuicaoCargo(
      Cypress.env("REGISTRO_FUNCIONAL"),
      Cypress.env("CARGO_CODIGO"),
    ).as("response");
  },
);

When(
  "realizo consulta de atribuição do funcionário por cargo com RF e código do cargo inexistentes",
  () => {
    cy.getFuncionarioAtribuicaoCargo(
      Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE"),
      Cypress.env("CARGO_CODIGO_INEXISTENTE"),
    ).as("response");
  },
);

When(
  "realizo consulta de atribuição do funcionário por cargo com formato de código do cargo inválido",
  () => {
    cy.getFuncionarioAtribuicaoCargo(
      Cypress.env("REGISTRO_FUNCIONAL"),
      Cypress.env("CARGO_CODIGO_FORMATO_INVALIDO"),
    ).as("response");
  },
);

And(
  "o retorno deve conter lista de atribuições do funcionário por cargo",
  listaCheck,
);

// GET /api/funcionarios/cargo/{registro_funcional}
When("realizo consulta de cargos do funcionário com RF válido", () => {
  cy.getFuncionarioCargos(Cypress.env("REGISTRO_FUNCIONAL")).as("response");
});

When("realizo consulta de cargos do funcionário com RF inexistente", () => {
  cy.getFuncionarioCargos(Cypress.env("REGISTRO_FUNCIONAL_INEXISTENTE")).as(
    "response",
  );
});

And("o retorno deve conter lista de cargos do funcionário", listaCheck);

// GET /api/funcionarios/cargos/{codigo_cargo}
When("realizo consulta de funcionários por código do cargo válido", () => {
  cy.getFuncionariosPorCodigoCargo(Cypress.env("CARGO_CODIGO")).as("response");
});

When("realizo consulta de funcionários por código do cargo inexistente", () => {
  cy.getFuncionariosPorCodigoCargo(Cypress.env("CARGO_CODIGO_INEXISTENTE")).as(
    "response",
  );
});

When(
  "realizo consulta de funcionários por código do cargo com formato inválido",
  () => {
    cy.getFuncionariosPorCodigoCargo("sasas").as("response");
  },
);

And("o retorno deve conter lista de funcionários por cargo", listaCheck);

// GET /api/funcionarios/funcionario-externo/{cpf}
When("realizo consulta de funcionário externo com CPF válido", () => {
  cy.getFuncionarioExterno(Cypress.env("CPF_FUNCIONARIO_EXTERNO")).as(
    "response",
  );
});

When("realizo consulta de funcionário externo com CPF inexistente", () => {
  cy.getFuncionarioExterno(Cypress.env("CPF_FUNCIONARIO_INEXISTENTE")).as(
    "response",
  );
});

And("o retorno deve conter dados do funcionário externo", dadosCheck);
