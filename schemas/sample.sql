-- ================================================================
-- Sample Database Schema: Company HR
-- This schema gives the AI agent context about your database
-- so it can generate accurate SQL queries.
-- ================================================================

-- Departments table
CREATE TABLE departments (
    department_id   INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    location        VARCHAR(100),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE employees (
    employee_id     INT PRIMARY KEY AUTO_INCREMENT,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    phone           VARCHAR(20),
    hire_date       DATE NOT NULL,
    job_title       VARCHAR(100),
    department_id   INT,
    manager_id      INT,
    is_active       BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Salaries table
CREATE TABLE salaries (
    salary_id       INT PRIMARY KEY AUTO_INCREMENT,
    employee_id     INT NOT NULL,
    amount          DECIMAL(12, 2) NOT NULL,
    currency        VARCHAR(3) DEFAULT 'USD',
    effective_date  DATE NOT NULL,
    end_date        DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Projects table
CREATE TABLE projects (
    project_id      INT PRIMARY KEY AUTO_INCREMENT,
    project_name    VARCHAR(200) NOT NULL,
    description     TEXT,
    start_date      DATE,
    end_date        DATE,
    budget          DECIMAL(15, 2),
    status          ENUM('planning', 'active', 'completed', 'cancelled') DEFAULT 'planning'
);

-- Employee-Project assignments (many-to-many)
CREATE TABLE project_assignments (
    assignment_id   INT PRIMARY KEY AUTO_INCREMENT,
    employee_id     INT NOT NULL,
    project_id      INT NOT NULL,
    role            VARCHAR(100),
    assigned_date   DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
