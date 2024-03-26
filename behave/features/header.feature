Feature: Evaluate response header for a specific endpoint.

  Background: Set endpoint and base URL
    Given I am using the endpoint "$APP_URL"
    And I set base URL to "/"

  @runner.continue_after_failed_step
  Scenario: Check response headers
    Given a set of specific headers:
      | key                       | value                    |
      | Strict-Transport-Security | max-age=31536000; includeSubDomains |
      | Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
      | Content-Security-Policy   | default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self'; base-uri 'none'; frame-ancestors 'none' |
      | X-Content-Type-Options    | nosniff |
      | X-Frame-Options           | SAMEORIGIN |
      | X-Frame-Options           | DENY |
      | Cache-Control             | no-cache |

    When I make a GET request to "WebGoat"
    Then the value of header "Cache-Control" should contain the defined value in the given set
    #And the the value of header "Strict-Transport-Security" should be in the given set
    #And the value of header "Content-Security-Policy" should be in the given set
    #And the value of header "X-Content-Type-Options" should be in the given set
    #And the value of header "X-Frame-Options" should be in the given set

