describe('Environment Check', function() {
    it('Environment Is Updated', function() {

        //NOTE: these parameters are passed in as CYPRESS_GRAFANA_USER and CYPRESS_GRAFANA_PASSWORD
        const user = Cypress.env('GRAFANA_USER')
        const pass = Cypress.env('GRAFANA_PASSWORD')

        expect(user).to.not.equal('')
        expect(pass).to.not.equal('')

        //TODO: add an assertion.  This will always pass as long as the cy.login() worked succesfully.

      })
  })
