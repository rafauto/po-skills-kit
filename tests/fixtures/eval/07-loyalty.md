<!-- request: "Marketing wants a points program, customers earn points and swap them for discounts and free baths" -->
# Earn loyalty points for completed appointments

As a returning pet owner, I want to earn points for every completed appointment, so that I am rewarded for coming back.

**Acceptance criteria**

Scenario: Points after a completed appointment
Given I completed an appointment that cost $50
When the salon marks the appointment as completed
Then 50 points are added to my balance
And I see the new balance on my profile

Scenario: Cancelled appointment
Given I cancelled an appointment
When the appointment date passes
Then no points are added to my balance

**Notes**
- Assumptions: 1 point per dollar spent.
- Open questions: do points expire?
- Suggested splits: redeeming points for discounts; redeeming points for a free bath.
- Quality check: lint_story 100/100, passed.
