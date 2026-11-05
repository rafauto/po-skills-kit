<!-- request: "Salons need to check vaccines before grooming, right now they ask for paper cards" -->
# Upload vaccination records before the appointment

As a pet owner booking a first visit, I want to upload my dog's vaccination record when booking, so that I don't need to bring paper cards to the salon.

**Acceptance criteria**

Scenario: Upload a valid file
Given I am booking a first visit
When I upload a PDF or photo of the vaccination record under 5 MB
Then the file is attached to the appointment
And the salon sees the record on the appointment details

Scenario: Unsupported file
Given I am booking a first visit
When I upload a file that is not a PDF, JPG or PNG
Then I see the message "Upload a PDF, JPG or PNG file"

**Notes**
- Assumptions: the salon, not the app, checks if vaccines are up to date.
- Open questions: how long do we keep the files (privacy)?
- Suggested splits: vaccine expiry alerts as a separate story.
- Quality check: lint_story 100/100, passed.
