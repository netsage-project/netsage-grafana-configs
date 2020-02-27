describe('Flow Analysis', function() {
    it('Flow Analysis', function() {

        cy.login()
        // Load dashboard
        cy.visit('http://localhost:3000/grafana/d/VuuXrnPWz/flow-analysis?orgId=1')
        cy.wait(5000)
        //TODO: add an assertion.  This will always pass as long as the cy.login() worked succesfully.

      })
  })
