/// <reference types="cypress" />
describe('Flow Analysis', () => {
    beforeEach(() => {
        cy.login()
        // Load dashboard
        cy.visit('http://localhost:3000/grafana/d/QfzDJKhik/flow-data-per-organization?orgId=1')
        cy.loadAllData()

    })
    it('ValidateFooter', () => {
        cy.validateFooter()
    })
    // it('Flow By Org', () => {
    //     console.log("Performing a flow analysis")
    //     console.log("Do something useful here")
    // })
})
