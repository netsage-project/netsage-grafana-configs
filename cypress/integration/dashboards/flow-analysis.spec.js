/// <reference types="cypress" />
describe('Flow Analysis', () => {
    beforeEach(() => {
        cy.login()
        // Load dashboard
        cy.visit('http://localhost:3000/grafana/d/VuuXrnPWz/flow-analysis?orgId=1')
        //TODO: can't identify scrolling element. so disabled for now.
        // cy.loadAllData()
    })
    // it('ValidateFooter', () => {
    //     cy.validateFooter()
    // })
    it('Flow Analysis', () => {
        console.log("Performing a flow analysis")
    })
})
