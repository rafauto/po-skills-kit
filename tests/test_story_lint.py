from po_skills_kit.story_lint import MAX_STORY_CHARS, format_report, lint_story

GOOD_STORY = """# Rebook in one tap

As a returning pet owner, I want to rebook my last grooming service in one tap,
so that I save time on routine appointments.

**Acceptance criteria**

- **Given** I had a grooming appointment in the last 6 months
- **When** I tap "Rebook"
- **Then** I see the same service and groomer with the next three free slots

Scenario: No past appointment
Given I never booked a service
When I open the home screen
Then the "Rebook" button is not shown
"""


def rules(result):
    return {finding.rule for finding in result.findings}


def test_good_story_passes_with_full_score():
    result = lint_story(GOOD_STORY)
    assert result.passed
    assert result.score == 100
    assert result.scenario_count == 2
    assert result.role == "returning pet owner"
    assert result.benefit == "I save time on routine appointments"


def test_missing_narrative_is_an_error():
    result = lint_story("Rebook button\n\nGiven a past visit\nWhen I tap\nThen I see slots")
    assert not result.passed
    assert "narrative-format" in rules(result)


def test_missing_acceptance_criteria_is_an_error():
    result = lint_story("As a pet owner, I want a waitlist, so that I get a slot.")
    assert "acceptance-criteria" in rules(result)
    assert not result.passed


def test_incomplete_scenario_names_the_missing_step():
    story = "As a pet owner, I want X, so that Y.\nGiven A\nWhen B\nThen C\nGiven D\nThen E"
    result = lint_story(story)
    messages = [f.message for f in result.errors]
    assert messages == ["Scenario 2 is missing: When."]


def test_and_steps_continue_the_previous_keyword():
    story = "As a pet owner, I want X, so that Y.\nGiven A\nAnd B\nWhen C\nThen D\nAnd E"
    result = lint_story(story)
    assert result.passed
    assert result.scenario_count == 1


def test_warnings_do_not_fail_the_story():
    story = "As a user, I want to pay and earn points, so that Y.\nGiven A\nWhen B\nThen it is fast"
    result = lint_story(story)
    assert result.passed
    assert rules(result) == {"specific-role", "single-goal", "testable-language"}
    assert result.score == 70


def test_large_stories_get_a_size_warning():
    scenarios = "\n".join(f"Scenario: {n}\nGiven A\nWhen B\nThen C" for n in range(7))
    result = lint_story(f"As a pet owner, I want X, so that Y.\n{scenarios}")
    assert "story-size" in rules(result)


def test_html_comments_are_ignored():
    result = lint_story(f"<!-- request: As a user I want everything -->\n{GOOD_STORY}")
    assert result.passed
    assert result.role == "returning pet owner"


def test_empty_and_oversized_input_are_rejected_without_raising():
    assert rules(lint_story("   ")) == {"input"}
    assert rules(lint_story("x" * (MAX_STORY_CHARS + 1))) == {"input"}


def test_report_lists_status_and_findings():
    report = format_report(lint_story("As a user, I want X, so that Y."), source="story.md")
    assert report.startswith("FAIL  story.md")
    assert "[error] acceptance-criteria" in report
