import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ========================================
// ACESSO API
// ========================================

Given("que possuo acesso à API de funcionários", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("REGISTRO_FUNCIONAL")).to.exist;
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
