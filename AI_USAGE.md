# AI Usage Disclosure

This document explains how AI tools were used while developing this assignment.

## 1. AI Tool(s) Used

* **ChatGPT**

  * Used to understand the assignment requirements, review the implementation, improve code quality, identify edge cases, and write test cases.
* **Cursor**

  * Used as an AI-assisted editor for code suggestions, refactoring, and improving project structure.

## 2. Prompts Given

Some of the prompts I used during development include:

* "Design a Django application for recommending the cheapest shipping box."
* "Review my packing algorithm and suggest improvements."
* "Identify weak points in my Django models and services."
* "Convert model fields from FloatField to DecimalField."
* "Write pytest test cases for models, solver, services, and API."
* "Review my README and improve its structure."
* "Review my implementation plan and suggest improvements."

## 3. Output Accepted

I accepted AI suggestions for:

* Initial Django project structure.
* Model validation improvements.
* Packing algorithm review and minor refactoring.
* Serializer and API improvements.
* Test case ideas and edge cases.
* Documentation structure for the README.

## 4. Output Rejected or Modified

I did not accept every AI suggestion directly. Some examples include:

* Rejected suggestions that introduced unnecessary complexity for the assignment.
* Modified generated code to match my project structure and coding style.
* Corrected template syntax issues before using the code.
* Simplified overly complex implementations to keep the solution readable and maintainable.

## 5. Mistakes Found in AI Output

While using AI assistance, I found several issues that required manual correction:

* Invalid Django template syntax in one response.
* Some generated code did not match my existing project structure.
* A few test cases required modification to work with my implementation.
* Decimal values stored inside `JSONField` caused serialization errors, which I fixed manually.
* Some suggested implementations were more complex than required for the assignment.

## 6. How I Verified the Final Code

I verified the final implementation by:

* Running the complete test suite using pytest.
* Testing the REST API endpoints manually.
* Testing the dashboard by creating sample orders.
* Verifying that the correct shipping box was selected for different scenarios.
* Reviewing the code manually to ensure the recommendation logic behaved as expected.

## 7. Manual Work

The following parts of the submission were completed manually:

* Project implementation and integration.
* Final code review and debugging.
* Test execution and verification.
* GitHub repository setup.
* Chat transcript export.
* Personal learning notes (LEARNINGS.md).

AI was used as a development assistant, but all generated code was reviewed, modified where necessary, and verified before submission.
