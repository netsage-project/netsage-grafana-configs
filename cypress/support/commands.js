// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
Cypress.Commands.add("login", () => {
    cy.visit('http://localhost:3000')

    // Login
    cy.get('input[name="username"]').type('admin')
    cy.get('input[name="password"]').type('admin')
    cy.get('button[ng-click="submit();"]')
        .click()

    // Skip reset password
    cy.get('a[ng-click="skip();"]')
        .click()

    // set Data source
    cy.visit('http://localhost:3000/grafana/datasources/edit/2')

    cy.get('input[ng-model="current.basicAuthUser"]').invoke('val').then((login) => {
        //Initialize DataSource only if not already set
        const new_login = Cypress.env('GRAFANA_USER')
        const new_passwd = Cypress.env('GRAFANA_PASSWORD')
        if (login === "" ) {
            cy.get('input[ng-model="current.basicAuthUser"]')
            .clear()
            .type(new_login)
            // set password
            cy.get('input[type="password"]')
            .clear()
            .type(new_passwd)
            //Save
            cy.get('button[class="btn btn-primary"]')
                .click()
            cy.wait(500)

        }
    });
})
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
