import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de DREs", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("DRE_CODIGO")).to.exist;
});

// LISTAGEM DE DRES
When("realizo consulta de listagem de DREs", () => {
  cy.getDREsLista().as("response");
});

// CONSULTA DE DRES POR LISTA DE CÓDIGOS
When("realizo consulta de DRE por lista de códigos", () => {
  cy.postDREsLista(true).as("response");
});

When("realizo consulta de DRE por lista de códigos não encontradas", () => {
  cy.postDREsLista(false).as("response");
});

// DETALHE DA DRE
When("realizo consulta de detalhe da DRE", () => {
  cy.getDREDetalhe(true).as("response");
});
When("realizo consulta de detalhe da DRE não encontrada", () => {
  cy.getDREDetalhe(false).as("response");
});

// ESCOLAS DE UMA DRE
When("realizo consulta de escolas da DRE", () => {
  cy.getDREsEscolas(true).as("response");
});
When("realizo consulta de escolas da DRE não encontrada", () => {
  cy.getDREsEscolas(false).as("response");
});

// ESCOLAS POR TIPO DE UNIDADE
When("realizo consulta de escolas por tipo", () => {
  cy.getDREsEscolasPorTipo(true).as("response");
});

// SUBPREFEITURAS
When("realizo consulta de subprefeituras da DRE", () => {
  cy.getDREsSubprefeituras(true).as("response");
});
When("realizo consulta de subprefeituras da DRE não encontrada", () => {
  cy.getDREsSubprefeituras(false).as("response");
});

// UES
When("realizo consulta de UEs da DRE", () => {
  cy.getDREsUEs(true).as("response");
});
When("realizo consulta de UEs da DRE não encontrada", () => {
  cy.getDREsUEs(false).as("response");
});

// UNIDADES
When("realizo consulta de unidades da DRE", () => {
  cy.getDREsUnidades(true).as("response");
});
When("realizo consulta de unidades da DRE não encontrada", () => {
  cy.getDREsUnidades(false).as("response");
});

// THEN - Status Codes
Then("retorna o status 200", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(200);
  });
});
Then("retorna o status 201", function () {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(201);
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

// AND - Validações de Retorno
And("o retorno deve conter lista de DREs", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoDRE");
        expect(response.body[0]).to.have.property("nomeDRE");
        expect(response.body[0]).to.have.property("siglaDRE");
      }
    }
  });
});

And("o retorno deve conter dados das DREs", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body[0]).to.have.property("codigoDRE");
      expect(response.body[0]).to.have.property("nomeDRE");
      expect(response.body[0]).to.have.property("siglaDRE");
      expect(response.body[0].codigoDRE).to.not.be.empty;
      expect(response.body[0].nomeDRE).to.not.be.empty;
    }
  });
});

And("o retorno deve conter dados da DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body[0]).to.have.property("codigoDRE");
      expect(response.body[0]).to.have.property("nomeDRE");
      expect(response.body[0]).to.have.property("siglaDRE");
      expect(response.body[0].codigoDRE).to.not.be.empty;
      expect(response.body[0].nomeDRE).to.not.be.empty;
    }
  });
});

And("o retorno deve conter lista de escolas da DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoEscola");
        expect(response.body[0]).to.have.property("nomeEscola");
      }
    }
  });
});

And("o retorno deve conter lista de subprefeituras da DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoSubprefeitura");
        expect(response.body[0]).to.have.property("nomeSubprefeitura");
      }
    }
  });
});

And("o retorno deve conter lista de UEs da DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body).to.be.an("array");
        expect(response.body).to.have.length.greaterThan(0);
      }
    }
  });
});

And("o retorno deve conter lista de unidades da DRE", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property("codigoEol");
        expect(response.body[0]).to.have.property("nomeOficial");
      }
    }
  });
});

And("o retorno deve ser uma lista vazia", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.be.an("array");
      expect(response.body.length).to.eq(0);
    }
  });
});
