<!-- request: "Customers want to see who will groom their dog and what they're good at" -->
# See groomer profiles before booking

As a first-time pet owner, I want to see each groomer's photo and specialties before booking, so that I can choose someone I trust with my dog.

**Acceptance criteria**

Scenario: Profile with specialties
Given the salon has three groomers
When I open the groomer list
Then I see each groomer's photo, name and specialties

Scenario: Profile without a photo
Given a groomer has no photo
When I open the groomer list
Then a placeholder image is shown in place of the photo

**Notes**
- Assumptions: groomers agree to publish their photo.
- Open questions: should reviews appear on the profile?
- Suggested splits: groomer reviews as a separate story.
- Quality check: lint_story 100/100, passed.
