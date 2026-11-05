<!-- request: "Regulars book the exact same thing every month, make it quicker" -->
# Rebook the last service in one tap

As a returning pet owner, I want to rebook my last grooming service in one tap, so that I don't fill in the same details every month.

**Acceptance criteria**

Scenario: Rebook with the same groomer
Given my last appointment was a full groom with Ana
When I tap "Rebook" on the home screen
Then I see the full groom with Ana preselected and her next three free slots

Scenario: Groomer no longer available
Given my last groomer left the salon
When I tap "Rebook"
Then the service is preselected and I am asked to choose another groomer

**Notes**
- Assumptions: "last service" means the most recent completed appointment.
- Open questions: none.
- Suggested splits: none.
- Quality check: lint_story 100/100, passed.
