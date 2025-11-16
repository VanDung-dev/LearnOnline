# Block Flow Diagram - LearnOnline Website

## Overview
```mermaid
graph TD
    A[User] --> B[Web Interface]
    B --> C[Django Application]
    C --> D[Database]
    C --> E[Static Files Server]
    C --> F[Media Storage]
    
    subgraph "Django Application Layers"
        C --> G[URL Routing]
        G --> H[Views Layer]
        H --> I[Business Logic]
        I --> J[Models/Data Access]
        J --> D
        I --> K[Authentication System]
        K --> J
        I --> L[Payment Processing]
        L --> J
    end
    
    subgraph "Main Functional Modules"
        C --> M[Accounts Management]
        C --> N[Courses Management]
        C --> O[Payments System]
    end
    
    subgraph "External Services"
        C --> P[TinyMCE Editor]
        C --> Q[Video Streaming]
    end
```

## Detailed Components

### 1. User Interface Layer
```mermaid
graph LR
    A[User] --> B[Browser]
    B --> C{Frontend}
    C --> D[HTML Templates]
    C --> E[CSS Styling]
    C --> F[JavaScript Functions]
    C --> G[Static Assets]
```

### 2. Authentication & Authorization System
```mermaid
graph TD
    A[Login Page] --> B[Authentication View]
    B --> C[Custom User Manager]
    C --> D[Profile Model]
    D --> E[User Roles]
    E --> F[Student]
    E --> G[Instructor]
    E --> H[Admin]
```

### 3. Course Management System
```mermaid
graph TD
    A[Course Catalog] --> B[Course Model]
    B --> C[Category]
    B --> D[Modules]
    D --> E[Lessons]
    E --> F[Lesson Types]
    F --> G[Text Content]
    F --> H[Video Content]
    F --> I[Quiz Content]
    
    J[Instructor Dashboard] --> K[Create/Edit Courses]
    K --> L[Module Ordering]
    K --> M[Lesson Management]
    M --> N[Quiz Builder]
```

### 4. Learning Process
```mermaid
graph TD
    A[Student Enrollment] --> B[Enrollment Model]
    B --> C[Progress Tracking]
    C --> D[Lesson Completion]
    C --> E[Quiz Attempts]
    E --> F[Score Calculation]
    
    G[Course Access] --> H[Module Unlocking]
    H --> I[Deadline Management]
    H --> J[Lock/Unlock Mechanism]
```

### 5. Payment System
```mermaid
graph TD
    A[Payment Request] --> B[Payment View]
    B --> C[Payment Model]
    C --> D[Transaction Processing]
    D --> E[Payment Status]
    E --> F[Course Enrollment]
    E --> G[Certificate Purchase]
```

### 6. Certificate System
```mermaid
graph TD
    A[Certificate Request] --> B[Certificate Model]
    B --> C[Completion Verification]
    C --> D[Certificate Generation]
    D --> E[Certificate Issuing]
```

## Data Flow

### User Registration Flow
```mermaid
graph LR
    A[Registration Form] --> B[Validation]
    B --> C[User Creation]
    C --> D[Profile Setup]
    D --> E[Role Assignment]
    E --> F[Dashboard Access]
```

### Course Enrollment Flow
```mermaid
graph LR
    A[Course Selection] --> B[Enrollment Check]
    B --> C[Payment Required?]
    C -->|Yes| D[Payment Process]
    C -->|No| E[Direct Enrollment]
    D --> E
    E --> F[Access Granted]
    F --> G[Progress Tracking Started]
```

### Learning Process Flow
```mermaid
graph LR
    A[Access Lesson] --> B[Check Access Rights]
    B --> C[Locked Content?]
    C -->|Yes| D[Purchase Required]
    C -->|No| E[Display Content]
    D --> E
    E --> F[Mark as Completed]
    F --> G[Update Progress]
```

### Quiz Taking Flow
```mermaid
graph LR
    A[Start Quiz] --> B[Load Questions]
    B --> C[Answer Questions]
    C --> D[Submit Answers]
    D --> E[Automatic Grading]
    E --> F[Store Results]
    F --> G[Show Score]
```

## Key Relationships

### Core Entity Relationships
```mermaid
graph TD
    User -->|hasOne| Profile
    User -->|hasMany| Enrollments
    User -->|hasMany| QuizAttempts
    User -->|hasMany| Payments
    User -->|hasMany| Certificates
    
    Course -->|belongsTo| Category
    Course -->|hasMany| Modules
    Course -->|hasMany| Enrollments
    Course -->|hasMany| Certificates
    
    Module -->|belongsTo| Course
    Module -->|hasMany| Lessons
    
    Lesson -->|belongsTo| Module
    Lesson -->|hasOne| Quiz
    Lesson -->|hasMany| ProgressRecords
    
    Quiz -->|belongsTo| Lesson
    Quiz -->|hasMany| Questions
    Quiz -->|hasMany| QuizAttempts
    
    Question -->|belongsTo| Quiz
    Question -->|hasMany| Answers
    Question -->|hasMany| UserAnswers
    
    Answer -->|belongsTo| Question
    
    QuizAttempt -->|belongsTo| User
    QuizAttempt -->|belongsTo| Lesson
    QuizAttempt -->|hasMany| UserAnswers
    
    UserAnswer -->|belongsTo| QuizAttempt
    UserAnswer -->|belongsTo| Question
    UserAnswer -->|hasMany| Answers
    
    Enrollment -->|belongsTo| User
    Enrollment -->|belongsTo| Course
    Enrollment -->|hasMany| Certificates
    Enrollment -->|hasMany| Payments
    
    Payment -->|belongsTo| User
    Payment -->|belongsTo| Course
    Payment -->|belongsTo| Enrollment
    
    Certificate -->|belongsTo| User
    Certificate -->|belongsTo| Course
    Certificate -->|belongsTo| Enrollment
```

## System Architecture
```mermaid
graph TD
    A[Client Tier] --> B[Web Server Tier]
    B --> C[Application Tier]
    C --> D[Database Tier]
    
    subgraph "Client Tier"
        A[Web Browser]
    end
    
    subgraph "Web Server Tier"
        B[Nginx/Apache]
    end
    
    subgraph "Application Tier"
        C1[Django Framework]
        C2[Static File Handler]
        C3[Media File Handler]
        C1 --> C2
        C1 --> C3
    end
    
    subgraph "Database Tier"
        D[(PostgreSQL/MySQL)]
    end
    
    C1 --> D
```