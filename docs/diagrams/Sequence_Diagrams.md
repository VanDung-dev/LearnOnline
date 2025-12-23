## Sequence Diagrams

### Student Enrolls in Course

#### 1. Student Authentication and Course Selection
```mermaid
sequenceDiagram
    actor Student
    participant System
    participant Course

    Student->>System: login()
    System-->>Student: authenticated
    Student->>System: browseCourses()
    System-->>Student: displayCourses()
    Student->>System: selectCourse(courseId)
    System->>Course: findById(courseId)
    Course-->>System: return course
    System-->>Student: showCourseDetails()
```

#### 2. Enrollment Process
```mermaid
sequenceDiagram
    actor Student
    participant System
    participant Enrollment

    System->>Enrollment: check(student, course)
    Enrollment-->>System: notEnrolled
    System->>Enrollment: create(student, course)
    Enrollment-->>System: enrollmentCreated
    System-->>Student: enrollmentSuccess()
```

### Instructor Creates Course with Modules and Lessons

#### 1. Instructor Authentication and Course Creation
```mermaid
sequenceDiagram
    actor Instructor
    participant System
    participant Course

    Instructor->>System: login()
    System-->>Instructor: authenticated
    Instructor->>System: createCourse(title, description)
    System->>Course: create(title, description, instructor)
    Course-->>System: courseCreated
    System-->>Instructor: courseDetails()
```

#### 2. Adding Modules and Lessons
```mermaid
sequenceDiagram
    actor Instructor
    participant System
    participant Module
    participant Lesson

    Instructor->>System: addModule(courseId, moduleTitle)
    System->>Module: create(courseId, title)
    Module-->>System: moduleCreated
    System-->>Instructor: moduleDetails()

    Instructor->>System: addLesson(moduleId, lessonTitle, type)
    System->>Lesson: create(moduleId, title, type)
    Lesson-->>System: lessonCreated
    System-->>Instructor: lessonDetails()
```

### Student Takes Quiz and Gets Certificate

#### 1. Quiz Taking Process
```mermaid
sequenceDiagram
    actor Student
    participant System
    participant Lesson
    participant Quiz
    participant Question
    participant Answer

    Student->>System: accessLesson(lessonId)
    System->>Lesson: findById(lessonId)
    Lesson-->>System: quizLesson
    System->>Quiz: findByLesson(lessonId)
    Quiz-->>System: quizWithQuestions
    System-->>Student: displayQuiz()

    Student->>System: submitAnswers(answers[])
    System->>Question: validateAnswers(answers[])
    Question-->>System: scores
    System->>Answer: calculateScore()
    Answer-->>System: finalScore
    System-->>Student: showScore()
```

#### 2. Certificate Generation
```mermaid
sequenceDiagram
    actor Student
    participant System
    participant Certificate

    System->>Certificate: checkCompletion(student, course)
    Certificate-->>System: completed
    System->>Certificate: generate(student, course)
    Certificate-->>System: certificateIssued
    System-->>Student: showCertificate()
```