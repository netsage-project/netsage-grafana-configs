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
    cy.get('input[name="user"]').type('admin')
    cy.get('input[name="password"]').type('admin')

    cy.get('button[class="css-q8s0r8-button"]').click()
    // cy.get('button[ng-click="submit();"]')

    // Skip reset password
    cy.get('a[aria-label="Skip change password button"]').click()

    // set Data source
    cy.visit('http://localhost:3000/grafana/datasources/edit/2')

    cy.get('input[placeholder="user"]').invoke('val').then((login) => {
        console.log(login)
        //Initialize DataSource only if not already set
        const new_login = Cypress.env('GRAFANA_USER')
        const new_passwd = Cypress.env('GRAFANA_PASSWORD')
        if (login === "") {
            cy.get('input[placeholder="user"]')
                .clear()
                .type(new_login)
            // set password
            cy.get('input[type="password"]')
                .clear()
                .type(new_passwd)
            //Save
            cy.get('button[class="btn btn-primary"]').click()
            cy.wait(500)

        }
    });
})

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
