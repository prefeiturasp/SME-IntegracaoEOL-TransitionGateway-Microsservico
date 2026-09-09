import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ========================================
// ACESSO API
// ========================================

Given("que possuo acesso à API de acessos", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("REGISTRO_FUNCIONAL")).to.exist;
});

// THEN
Then("retorna o status {int}", (statusCode) => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(statusCode);
  });
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
