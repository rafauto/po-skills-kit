<!-- request: "Some users asked for dark mode" -->
# Use the app in dark mode

As a pet owner who uses the app at night, I want to switch the app to dark mode, so that the screen is comfortable to read in low light.

**Acceptance criteria**

Scenario: Follow the phone setting
Given my phone is set to dark mode
When I open the app
Then the app uses the dark theme

Scenario: Manual choice
Given my phone is set to light mode
When I choose "Dark" in the app settings
Then the app uses the dark theme until I change the setting

**Notes**
- Assumptions: none.
- Open questions: which persona asked for it, and how many requests do we have?
- Suggested splits: none.
- Quality check: lint_story 100/100, passed.
