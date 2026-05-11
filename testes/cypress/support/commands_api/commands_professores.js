Cypress.Commands.add('getFuncionarioAtivo', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/acessos/funcionario-ativo/${Cypress.env('REGISTRO_FUNCIONAL')}/`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add('getNomeServidor', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/funcionarios/nome-servidor/${Cypress.env('REGISTRO_FUNCIONAL')}/`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add('getProfessorValidade', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/professores/${Cypress.env('REGISTRO_FUNCIONAL')}/validade/`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add('getProfessorPorRF', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/professores/${Cypress.env('REGISTRO_FUNCIONAL')}/`,
    headers: {
      accept: 'application/json',
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  });
});