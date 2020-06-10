/// <reference types="cypress" />
//import { e2e } from '@grafana/e2e';

import Chance from 'chance' // used to autogen data
const chance = new Chance()

describe('Flow Analysis', () => {
    beforeEach(() => {
        cy.login()
        // Load dashboard
        cy.visit('http://localhost:3000/grafana/d/VuuXrnPWz/flow-analysis?orgId=1')
        cy.wait(5000)

    })
    it('Flow Analysis', () => {
        console.log("Performing a flow analysis")
        expect(2).equals(2)

    })
    it('Another test', () => {
        console.log("woot another test")

    })
})
