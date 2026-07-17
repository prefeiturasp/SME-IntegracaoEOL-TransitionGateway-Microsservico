import { Given, When, Then, And } from "cypress-cucumber-preprocessor/steps";

// ACESSO API
Given("que possuo acesso à API de componentes curriculares", () => {
  expect(Cypress.env("API_URL")).to.exist;
  expect(Cypress.env("API_KEY_HEADER")).to.exist;
  cy.log(
    "Acesso à API de componentes curriculares garantido via API_KEY configurada no ambiente",
  );
});

When(
  "realizo consulta de agrupamentos correlacionados de território do saber para um componente curricular válido",
  () => {
    cy.getAgrupamentosCorrelacionadosPorComponente(true).as("response");
  },
);

When(
  "realizo consulta de agrupamentos correlacionados de território do saber para um componente curricular inválido",
  () => {
    cy.getAgrupamentosCorrelacionadosPorComponente(false).as("response");
  },
);

When(
  "realizo envio de agrupamentos correlacionados de território do saber com códigos válidos",
  () => {
    cy.postAgrupamentosCorrelacionados(true).as("response");
  },
);

When(
  "realizo envio de agrupamentos correlacionados de território do saber com códigos inválidos",
  () => {
    cy.postAgrupamentosCorrelacionados(false).as("response");
  },
);

When(
  "realizo envio de agrupamentos de território do saber com códigos válidos",
  () => {
    cy.postAgrupamentos(true).as("response");
  },
);

When(
  "realizo envio de agrupamentos de território do saber com códigos inválidos",
  () => {
    cy.postAgrupamentos(false).as("response");
  },
);

Then("retorna o status 200", () => {
  cy.get("@response").then((response) => {
    expect(response.status).to.eq(200);
  });
});

And(
  "o retorno deve conter lista de agrupamentos correlacionados de território do saber",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.be.an("array");
        if (response.body.length > 0) {
          expect(response.body).to.be.an("array");
          expect(response.body).not.be.empty;
        }
      }
    });
  },
);

And(
  "o retorno deve conter lista de agrupamentos de território do saber",
  () => {
    cy.get("@response").then((response) => {
      if (response.status === 200) {
        expect(response.body).to.be.an("array");
        if (response.body.length > 0) {
          expect(response.body).to.be.an("array");
          expect(response.body).not.be.empty;
        }
      }
    });
  },
);

When("realizo consulta ao catalogo de componentes curriculares", () => {
  cy.getComponentesCurriculares().as("response");
});

When("realizo consulta a grade curricular do ano letivo de 2026", () => {
  cy.getGradeComponentesCurriculares().as("response");
});

When("realizo consulta aos componentes de regencia do ano de turma 1", () => {
  cy.getComponentesRegencia().as("response");
});

When("realizo consulta aos componentes do funcionario 7907206 no perfil 1", () => {
  cy.getComponentesFuncionarioPorPerfil().as("response");
});

When("realizo consulta aos componentes da turma 2855275 sem planejamento", () => {
  cy.getComponentesPorTurma().as("response");
});

And("o retorno deve conter uma lista de componentes curriculares", () => {
  cy.get("@response").then((response) => {
    expect(response.body).to.be.an("array");
  });
});

And("os componentes do catalogo devem conter codigo e descricao", () => {
  cy.get("@response").then((response) => {
    if (response.body.length > 0) {
      expect(response.body[0]).to.include.keys("codigo", "descricao");
    }
  });
});

And("a grade curricular deve conter dados do componente e da serie", () => {
  cy.get("@response").then((response) => {
    if (response.body.length > 0) {
      expect(response.body[0]).to.include.keys(
        "codigoComponenteCurricular",
        "descricaoComponenteCurricular",
        "codigoAnoTurma",
      );
    }
  });
});

And("os componentes de regencia devem conter o ano da turma", () => {
  cy.get("@response").then((response) => {
    if (response.body.length > 0) {
      expect(response.body[0]).to.include.keys("codigo", "anoTurma");
    }
  });
});

And("os componentes detalhados devem conter codigo e regencia", () => {
  cy.get("@response").then((response) => {
    if (response.body.length > 0) {
      expect(response.body[0]).to.include.keys("codigo", "regencia");
    }
  });
});
