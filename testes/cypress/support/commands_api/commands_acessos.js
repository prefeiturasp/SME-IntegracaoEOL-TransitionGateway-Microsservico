Cypress.Commands.add("getFuncionarioAtivo", (valor) => {
  let ativo =
    valor === true ? `${Cypress.env("REGISTRO_FUNCIONAL")}` : "0000000";
  return cy.request({
    method: "GET",
    url: `${Cypress.env("API_URL")}/api/acessos/funcionario-ativo/${ativo}/`,
    headers: {
      accept: "application/json",
      [Cypress.env("API_KEY_HEADER")]: Cypress.env("API_KEY"),
    },
    failOnStatusCode: false,
  });
});
