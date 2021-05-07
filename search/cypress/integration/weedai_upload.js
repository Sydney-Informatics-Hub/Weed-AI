describe('Test the overallworkflow', function () {

    beforeEach(() => {
        cy.visit('http://localhost/upload', {failOnStatusCode: false})
        cy.get('#sign_in_button').click()
        cy.get('#username')
          .type('admin')
          .should('have.value', 'admin')
        cy.get('#password')
          .type('password')
          .should('have.value', 'password')
        cy.get('#sign_in_submit').submit()
    })
    it('Test Weedcoco Upload', function () {
        cy.get('#annotation_format').type('weedcoco{enter}')
        cy.get('#upload_button').click()
        cy.get('.dzu-input').attachFile('test_weedcoco/weedcoco.json')
        cy.get('#next_and_submit').click()
        cy.get('div.fileContainer > input').attachFile('test_weedcoco/images/001_image.png')
        cy.get('#next_and_submit').click()
        cy.get('#sign_out_button').click()
    })
})