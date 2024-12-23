# To-Do List

Most of the tasks are also tracked in Odoo.

## Authentication App
- Clarify the functionality and purpose of the authentication app.
- Remove the **Tokenauth** feature and retain the standard password-based model.
- If feasible, group related apps into a single package to streamline the project structure and ensure logical organization.

## Course App
- Develop the Course app with the following structure:
  - **Learning Path** > **Unit** > **Lesson** > **Exercise** > **Exercise Type**
- Ensure the **Learning Path** accommodates multiple languages supported by the SaaS platform.  
  - This field should reference the `target_language` field (English, French, Dutch, Spanish) defined in the **Authentication App** under the `User` class.
