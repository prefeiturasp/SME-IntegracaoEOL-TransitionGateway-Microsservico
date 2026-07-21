Cypress.Commands.add(
  "getAgrupamentosCorrelacionadosPorComponente",
  (valido) => {
    let codigoComponente =
      valido === true ? `${Cypress.env("COD_AGRUPAMENTO")}` : "0000000";
    return cy.request({
      method: "GET",
      url: `${Cypress.env(
        "API_URL",
      )}/api/v1/componentes-curriculares/${codigoComponente}/territorio-saber/agrupamentos-correlacionados/`,
      headers: {
        accept: "application/json",
        [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      },
      failOnStatusCode: false,
    });
  },
);

Cypress.Commands.add("postAgrupamentosCorrelacionados", (valor) => {
  let lista =
    valor === true ? `${Cypress.env("LISTA_COD_AGRUPAMENTO")}` : '["000000"]';
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/territorio-saber/agrupamentos-correlacionados/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
    },
    body: `${lista}`,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("postAgrupamentos", (valor) => {
  let lista =
    valor === true ? `${Cypress.env("LISTA_COD_AGRUPAMENTO")}` : '["000000"]';
  return cy.request({
    method: "POST",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/territorio-saber/agrupamentos/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
      "Content-Type": "application/json",
      "X-CSRFTOKEN": Cypress.env("CSRF_TOKEN"),
    },
    body: `${lista}`,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesCurriculares", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getGradeComponentesCurriculares", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/v1/componentes-curriculares/ano-turma/ano-letivo/${Cypress.env(
      "ANO_LETIVO",
    )}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesRegencia", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/anos/1/regencia/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesFuncionarioPorPerfil", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env(
      "API_URL",
    )}/api/v1/componentes-curriculares/funcionarios/${Cypress.env("REGISTRO_FUNCIONAL")}/perfis/1/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesPorTurma", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/`,
    qs: {
      adicionarComponentesPlanejamento: false,
      codigoTurmas: `${Cypress.env("TURMA_CODIGO")}`,
    },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getDadosAulaTurma", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/dados-aula-turma/`,
    qs: {
      ueCodigo: Cypress.env("UE_CODIGO"),
      anoLetivo: Cypress.env("ANO_LETIVO"),
      componentesCurriculares: Cypress.env("COMPONENTE_CURRICULAR"),
    },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesTurmaFuncionario", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/${Cypress.env("TURMA_CODIGO")}/funcionarios/${Cypress.env("REGISTRO_FUNCIONAL")}/perfis/1/agrupaComponenteCurricular/true/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesPlanejamento", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/${Cypress.env("TURMA_CODIGO")}/funcionarios/${Cypress.env("REGISTRO_FUNCIONAL")}/perfis/1/planejamento/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getValidacaoComponentePap", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/${Cypress.env("TURMA_CODIGO")}/funcionarios/${Cypress.env("REGISTRO_FUNCIONAL")}/perfis/1/validar/pap/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesSemAtribuicao", (valor) => {
  let codigo_turma =
    valor === true ? `${Cypress.env("TURMA_CODIGO")}` : "000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/${codigo_turma}/sem-atribuicao/639038592000000000/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesTurmasRegulares", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/turmas/regulares/`,
    qs: { codigoTurmas: Cypress.env("TURMA_CODIGO") },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesTurmasPrograma", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/ues/${Cypress.env("UE_CODIGO")}/modalidades/${Cypress.env("MODALIDADE")}/anos/${Cypress.env("ANO_LETIVO")}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesUeAnosEscolares", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/ues/${Cypress.env("UE_CODIGO")}/modalidades/${Cypress.env("MODALIDADE")}/anos/${Cypress.env("ANO_LETIVO")}/anos-escolares/`,
    qs: { anosEscolares: Cypress.env("ANO_ESCOLAR") },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("getComponentesTurmasUe", () => {
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/v1/componentes-curriculares/ues/${Cypress.env("UE_TURMAS_CODIGO")}/turmas/`,
    qs: { turmas: Cypress.env("TURMA_CODIGO") },
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
