# Reschedule an appointment without calling

As a pet owner with a booked grooming appointment, I want to reschedule it in the app, so that I don't have to call the salon during working hours.

**Acceptance criteria**

Scenario: Reschedule to a free slot
Given I have an appointment more than 24 hours away
When I pick a new free slot and confirm
Then the appointment moves to the new slot
And I receive a confirmation message with the new date and time

Scenario: Too close to the appointment
Given my appointment starts in less than 24 hours
When I try to reschedule it
Then I see the salon's phone number and the message "Changes within 24 hours must be made by phone"
