/// <reference types="cypress" />
describe('Bandwidth Dashboard', () => {
    beforeEach(() => {
        cy.login()
        // Load dashboard
        cy.visit('http://localhost:3000/grafana/d/000000003/bandwidth-dashboard?orgId=1')
        cy.loadAllData()

    })
    it('ValidateFooter', () => {
        cy.validateFooter()
    })
})
