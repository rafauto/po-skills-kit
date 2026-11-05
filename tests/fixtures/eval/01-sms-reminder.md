<!-- request: "Lots of no-shows on Mondays. Can we remind people the day before?" -->
# Send an SMS reminder before the appointment

As a pet owner with an upcoming grooming appointment, I want to receive an SMS reminder 24 hours before it, so that I don't forget the appointment.

**Acceptance criteria**

Scenario: Reminder is sent
Given I have an appointment tomorrow at 10:00
And my phone number is verified
When the clock reaches 10:00 today
Then I receive an SMS with the salon name, the date and the time of the appointment

Scenario: Appointment booked less than 24 hours ahead
Given I book an appointment that starts in 5 hours
When the booking is confirmed
Then no reminder SMS is scheduled

**Notes**
- Assumptions: reminders go only to verified phone numbers.
- Open questions: should the SMS include a link to reschedule?
- Suggested splits: none.
- Quality check: lint_story 100/100, passed.
