<!-- request: "Salons want people to pay when they book so they stop losing money on no-shows." -->
# Pay for the appointment when booking

As a pet owner booking a grooming appointment, I want to pay by card during booking, so that my appointment is confirmed right away.

**Acceptance criteria**

Scenario: Successful payment
Given I selected a service and a free slot
When I enter valid card details and confirm
Then the appointment status changes to "Confirmed"
And I receive a receipt by email

Scenario: Card declined
Given I selected a service and a free slot
When my card is declined
Then I see the message "Your card was declined. Try another card."
And the slot stays free for other pet owners

**Notes**
- Assumptions: the salon has a payment account set up.
- Open questions: is a partial deposit enough for some salons?
- Suggested splits: refunds on cancellation as a separate story.
- Quality check: lint_story 100/100, passed.
