import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de escolas", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  expect(Cypress.env("UE_CODIGO")).to.exist;
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
And("o retorno deve conter dados da escola", () => {
  cy.get("@response").then((response) => {
    if (response.status === 200) {
      expect(response.body).to.have.property("codigoEscola");
      expect(response.body).to.have.property("nomeEscola");
      expect(response.body).to.have.property("nomeDRE");
      expect(response.body.codigoEscola).to.not.be.empty;
      expect(response.body.nomeEscola).to.not.be.empty;
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
