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
// FUNCIONÁRIO ATIVO
// ========================================

When("realizo consulta de funcionário ativo", () => {
  cy.getFuncionarioAtivo(true).as("response");
});

When("realizo consulta de funcionário não ativo", () => {
  cy.getFuncionarioAtivo(false).as("response");
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
