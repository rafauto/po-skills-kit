<!-- request: "Saturdays are always full, people ask to be called if something opens up" -->
# Join the waitlist for a fully booked day

As a pet owner who wants a Saturday appointment, I want to join the waitlist for a fully booked day, so that I can get a slot if someone cancels.

**Acceptance criteria**

Scenario: Join the waitlist
Given every slot on Saturday is booked
When I tap "Join waitlist" for Saturday
Then I see my position on the waitlist

Scenario: A slot opens up
Given I am first on the Saturday waitlist
When another pet owner cancels a Saturday appointment
Then I receive a notification offering the free slot for 30 minutes

**Notes**
- Assumptions: the offer expires after 30 minutes and moves to the next person.
- Open questions: how long can the waitlist be?
- Suggested splits: none.
- Quality check: lint_story 100/100, passed.
