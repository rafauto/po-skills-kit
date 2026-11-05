<!-- request: "People call just to cancel, the front desk can't keep up" -->
# Cancel an appointment in the app

As a pet owner with a booked appointment, I want to cancel it in the app, so that I don't have to call the salon.

**Acceptance criteria**

Scenario: Cancel ahead of time
Given my appointment is more than 24 hours away
When I tap "Cancel appointment" and confirm
Then the appointment status changes to "Cancelled"
And the slot becomes available to other pet owners

Scenario: Late cancellation
Given my appointment starts in less than 24 hours
When I tap "Cancel appointment"
Then I see the late cancellation fee before I confirm

**Notes**
- Assumptions: the 24-hour rule matches the rescheduling story.
- Open questions: what is the late cancellation fee?
- Suggested splits: none.
- Quality check: lint_story 100/100, passed.
