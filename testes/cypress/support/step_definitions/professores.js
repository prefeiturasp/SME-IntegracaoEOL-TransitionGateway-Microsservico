import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

// ========================================
// ACESSO API
// ========================================

Given('que possuo acesso à API de professores', () => {

  expect(Cypress.env('API_URL')).to.exist
  expect(Cypress.env('API_KEY')).to.exist
  expect(Cypress.env('API_KEY_HEADER')).to.exist
  expect(Cypress.env('REGISTRO_FUNCIONAL')).to.exist

})

// ========================================
// FUNCIONÁRIO ATIVO
// ========================================

When('realizo consulta de funcionário ativo', () => {

  cy.getFuncionarioAtivo()
    .as('response')

})

Then('o retorno deve ser booleano', () => {

  cy.get('@response').then((response) => {

    expect(response.status).to.be.oneOf([200, 204])

    if (response.status === 200) {

      expect(response.body).to.be.a('boolean')

    }

  })

})

// ========================================
// NOME SERVIDOR
// ========================================

When('realizo consulta de nome do servidor', () => {

  cy.getNomeServidor()
    .as('response')

})

Then('o retorno deve conter nome e cpf', () => {

  cy.get('@response').then((response) => {

    expect(response.status).to.be.oneOf([200, 204])

    if (response.status === 200) {

      expect(response.body).to.have.property('nome')
      expect(response.body).to.have.property('cpf')

      expect(response.body.nome).to.not.be.empty
      expect(response.body.cpf).to.not.be.empty

    }

  })

})

// ========================================
// PROFESSOR VÁLIDO
// ========================================

When('realizo consulta de validade do professor', () => {

  cy.getProfessorValidade()
    .as('response')

})

// ========================================
// PROFESSOR POR RF
// ========================================

When('realizo consulta de professor por RF', () => {

  cy.getProfessorPorRF()
    .as('response')

})

Then('o retorno deve conter o nome do professor', () => {

  cy.get('@response').then((response) => {

    expect(response.status).to.be.oneOf([200, 204])

    if (response.status === 200) {

      expect(response.body).to.exist
      expect(response.body).to.be.a('string')

    }

  })

})

// ========================================
// STATUS PADRÃO
// ========================================

Then('o status da resposta deve ser válido para professores', () => {

  cy.get('@response').then((response) => {

    expect(response.status).to.be.oneOf([200, 204])

  })

})

// ========================================
// RETORNO PADRÃO
// ========================================

Then('o retorno deve ser válido', () => {

  cy.get('@response').then((response) => {

    expect(response).to.exist
    expect(response).to.have.property('status')

    if (response.status === 200) {

      expect(response.body).to.exist

    }

  })

})