import "@shelex/cypress-allure-plugin";

// Comandos
import "./commands_api/commands_professores";
import "./commands_api/commands_alunos";
import "./commands_api/commands_escolas";
import "./commands_api/commands_turmas";
import "./commands_api/commands_funcionarios";
import "./commands_api/commands_dres";
import "./commands_api/commands_componentes_curriculares";
import "./commands_api/commands_abrangencia";
import "./commands_api/commands_acessos";

// Evita quebra de teste
Cypress.on("uncaught:exception", () => false);
