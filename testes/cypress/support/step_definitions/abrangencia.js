import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de abrangência", () => {
  expect(Cypress.env("API_URL")).to.exist;
  cy.log(
    "Acesso à API de abrangência garantido via API_KEY configurada no ambiente",
  );
});

// THEN
Then("retorna o status {int}", (statusCode) => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(statusCode);
  });
});

// WHEN
// Endpoint GET - /api/abrangencia/estrutura-vigente/{codigoDre}
When("realizo consulta de estrutura vigente pelo código DRE válido", () => {
  cy.getAbrangenciaEstruturaVigente(Cypress.env("DRE_CODIGO")).as("response");
});

When(
  "realizo consulta de estrutura vigente pelo código DRE inexistente",
  () => {
    cy.getAbrangenciaEstruturaVigente(Cypress.env("DRE_CODIGO_INEXISTENTE")).as(
      "response",
    );
  },
);

// Endpoint POST - /api/abrangencia/estrutura-vigente
When("realizo envio de estrutura vigente com filtro de turmas válido", () => {
  cy.postAbrangenciaEstruturaVigente(true).as("response");
});

When(
  "realizo envio de estrutura vigente com filtro de turmas inexistente",
  () => {
    cy.postAbrangenciaEstruturaVigente(false).as("response");
  },
);

And("o retorno deve conter dados de estrutura vigente", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.exist;
      expect(response.body).to.not.be.empty;
    }
  });
});
