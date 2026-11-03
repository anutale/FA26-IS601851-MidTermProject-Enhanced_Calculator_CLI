"""
Enhanced Calculator: Application Entry Point
===========================================

This module serves as the startup point for the calculator application.
It is intentionally lightweight: its job is to import the interactive
command-line loop and launch it when the program is run directly.

The project is designed as an educational demonstration of advanced
Python programming concepts, especially object-oriented design and
software architecture. The calculator is not just a simple arithmetic
utility; it models a larger system with reusable components for:

- command handling and user interaction
- arithmetic calculation strategies
- input validation and error management
- state persistence and undo/redo behavior through mementos
- configuration and operational settings
- calculation history tracking and retrieval
- testable, modular application logic

Program Flow
------------
When executed with:

    python main.py

Python loads this module, imports the REPL entry function from the
app package, and starts the calculator interface. All actual business
logic and supporting classes live under the app directory so that the
entry point remains clear and easy to understand.

Architecture Notes
------------------
This file acts as the top-level launcher for the application and keeps
responsibility separation intact. The wider project follows a modular
structure where each component has a specific role, making the codebase
easier to maintain, test, and extend.

Version: 1.0
"""





from app.calculator_repl import calculator_repl


if __name__ == "__main__":
    calculator_repl()