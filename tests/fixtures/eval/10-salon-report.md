<!-- request: "Salon owners want to know how the week went, bookings, no-shows, revenue, everything" -->
# See the weekly bookings summary

As a salon owner, I want to see a weekly summary of bookings and no-shows, so that I can plan staff for the next week.

**Acceptance criteria**

Scenario: Weekly summary
Given the salon had 40 bookings and 3 no-shows last week
When I open the "Weekly summary" page on Monday
Then I see 40 bookings, 3 no-shows and a no-show rate of 7.5%

Scenario: First week with no data
Given the salon joined this week
When I open the "Weekly summary" page
Then I see the message "Your first summary will be ready next Monday"

**Notes**
- Assumptions: the week runs from Monday to Sunday.
- Open questions: which other numbers matter most ("everything" is too broad)?
- Suggested splits: revenue summary as a separate story.
- Quality check: lint_story 100/100, passed.
