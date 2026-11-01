# 🚀 VIDHYASTRA -- Adaptive Learning Platform

## 👨‍💻 JUDGES: START HERE

**Main application file: `app.py`**

To run the Vidhyastra website:

``` bash
python app.py
```

Then open your browser and visit:

<http://127.0.0.1:5000/>

**Technology:** Python, Flask, SQLite, HTML, CSS and JavaScript.

Please refer to the sections below for project details, features and
setup instructions.

------------------------------------------------------------------------

## 1. Demo Access for Judges

### Platform Administrator

The application creates the shared demonstration platform-admin account
when the database is initialized.

-   **Username / email:** `platform.admin@vidhyastra.demo`
-   **Demo password:** `VidhyastraDemo@2026`
-   **Login:** Open the website and choose Login. After successful
    sign-in, platform administrators are routed to the platform
    dashboard.

**Security note:** These are shared demonstration credentials, not
production credentials. They are included for this public project
demonstration. Do not use this account for real student data or a
production deployment. Change or disable the shared demo password before
public production use.

### School codes for student and parent registration

  School                   Registration school code
  ------------------------ --------------------------
  Vidhyastra Demo School   `VDS-DEMO`
  HA2026 School            `HA2026`
  Heisenberg School        `HEISENBERG`

School-code input is normalized to uppercase, so entering `Heisenberg`
or `HEISENBERG` is treated as the same code. The accompanying
`enable_demo_schools.py` script updates `app.py` so these school records
are created automatically when the application initializes its database.
Existing school records and user links are preserved.

------------------------------------------------------------------------

## 2. Project Overview

Vidhyastra is a web-based learning and quiz platform designed to help
students access curriculum content, practise questions, attempt quizzes
and review their performance through a student-friendly interface.

The application combines a browser-based frontend, a Python Flask
backend, question-bank modules and a database to support the learning
workflow.

## 3. How the Website Works

Vidhyastra follows a client-server structure:

1.  A student opens the website in a browser.
2.  HTML templates define the page structure and forms. CSS controls the
    appearance and layout. JavaScript supports browser-side interactions
    where used.
3.  The browser sends page requests and form submissions to the Flask
    application.
4.  Python code in `app.py` handles application routes and connects the
    website pages to the relevant curriculum, quiz and account
    functions.
5.  Curriculum modules organise available grade, subject and chapter
    information.
6.  Question-bank modules provide the quiz questions used by the
    application.
7.  SQLite stores application records used by the website.
8.  Flask returns the requested page or quiz result to the browser.

**Basic flow:** Student → Browser interface → Flask (`app.py`) →
Curriculum and question-bank modules → Database (when needed) → Response
displayed in the browser.

## 4. Technologies Used

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Main programming language for
                                      application logic

  Flask                               Web framework that handles routes
                                      and connects the frontend with
                                      Python code

  HTML                                Defines the structure of website
                                      pages

  CSS                                 Styles the pages, layouts, colours
                                      and visual elements

  JavaScript                          Supports interactive behaviour in
                                      the browser

  SQLite                              Lightweight database used for
                                      application data

  JSON                                Stores structured question-bank
                                      data
  -----------------------------------------------------------------------

## 5. Important Project Files

  -----------------------------------------------------------------------
  File or folder                      Purpose
  ----------------------------------- -----------------------------------
  `app.py`                            Main Flask application and starting
                                      point of the website

  `templates/`                        HTML templates used to display
                                      website pages

  `static/`                           Static assets such as CSS,
                                      JavaScript and images

  `question_bank.py`                  Loads and provides question-bank
                                      data to the application

  `question_bank.json`                Structured quiz question data

  `curriculum_catalog.py`             Curriculum and chapter information

  `class6_content.py`                 Class 6 question content

  `class6_quiz.py`                    Class 6 quiz-related functionality

  `class8_content.py`                 Class 8 question content

  `vidhyastra.db`                     SQLite database used by the
                                      application
  -----------------------------------------------------------------------

The repository may also contain helper scripts, backup files and tests.
The files above are the main files relevant to understanding and running
the website.

## 6. Main Website Features

-   Student registration and login.
-   Student dashboard and profile pages.
-   Curriculum browsing by class, subject and chapter, where configured.
-   Quiz screens for attempting available practice questions.
-   Answer evaluation and quiz-result display.
-   Progress and performance information shown in the student interface.
-   Platform administration for managing school records.
-   Separate curriculum and question-content modules to keep learning
    content organised.

The subjects, chapters and quiz availability depend on the content
configured in the project.

## 7. How to Install and Run

### Requirements

-   Python 3.
-   The Vidhyastra project files.
-   The packages listed in `requirements.txt`.

### Install dependencies

Open a terminal in the project folder and run:

``` bash
python -m pip install -r requirements.txt
```

### Start the application

From the same project folder, run:

``` bash
python app.py
```

Keep the terminal open while using the website. When Flask starts
successfully, open:

<http://127.0.0.1:5000/>

To stop the local server, return to the terminal and press `Ctrl + C`.

**Important:** `127.0.0.1` is a local development address. It works on
the computer running the Flask application and is not a public website
link. Judges using another computer will need a publicly deployed URL to
access the website.

## 8. Project Structure

``` text
Vidhyastra_MVP/
├── app.py
├── requirements.txt
├── question_bank.py
├── question_bank.json
├── curriculum_catalog.py
├── class6_content.py
├── class6_quiz.py
├── class8_content.py
├── templates/
├── static/
└── vidhyastra.db
```

Some files may be added or updated as the project develops.

## 9. Project Purpose

Vidhyastra aims to make learning practice and revision easier to access
through a single student-focused website. Its modular structure
separates the web application, page templates, curriculum information,
question content and stored application data.

------------------------------------------------------------------------

**Project:** Vidhyastra -- Adaptive Learning Platform\
**Main application file:** `app.py`\
**GitHub repository:**
[Vidhyastra_MVP](https://github.com/LokeshKulkarni-02/Vidhyastra_MVP)
