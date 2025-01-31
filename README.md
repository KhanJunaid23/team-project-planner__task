# Team Project Planner Tool

This project implements a team project planner tool with APIs for managing users, teams, and tasks within a team board. The implementation uses local file storage for persistence, with JSON files stored in the `db` directory.

## Choices and Assumptions
The design of the system is guided by thoughtful choices and assumptions to ensure efficiency and maintainability. JSON files are used for data persistence due to their simplicity and ease of debugging, allowing straightforward storage and retrieval of information. To maintain robustness, comprehensive input validation is implemented, and exceptions are raised for invalid inputs, ensuring proper error handling. The code structure emphasizes modularity, incorporating base classes and concrete implementations to promote clarity, reusability, and future extensibility.