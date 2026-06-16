import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

Given("que possuo acesso à API de turmas", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("CODIGO_TURMA")).to.exist;
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
      expect(response.body).to.not.be.empty;
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
