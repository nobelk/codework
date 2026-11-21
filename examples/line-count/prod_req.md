# Line Count product requirements

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-11-21 |
| **Target release** | Phase 1 |
| **Participants** | Product owner and developer |
| **System name** | Line Count |
| **Sources** | [Line Count brief](brief.md) |

## 1. Background and strategic fit

### 1.1 Problem

Developers need to confirm the expected line count of a local text fixture. Manual counting can miss a blank line or an unterminated final line.

### 1.2 Strategic fit

A single local command makes the count repeatable in the first release.

## 2. Goals and success metrics

| ID | Goal | Metric | Baseline | Target |
|---|---|---|---|---|
| G1 | Make fixture line counts repeatable | Correct output on the agreed line fixtures | No command | 4 of 4 fixtures at Phase 1 |

## 3. Users

| User | Who they are | What they come to do | How often |
|---|---|---|---|
| Developer | Maintainer of text fixtures | Check the line count before updating a test | During fixture changes |

## 4. Scope

### 4.1 In scope

- Count the lines in one local text file.
- Report invalid or inaccessible input with a failure exit status.

### 4.2 What we're not doing

- Multiple files, standard input, and recursion are outside the first phase.

## 5. User stories

| ID | User story | Priority | Goals |
|---|---|---|---|
| US1 | As a developer, I want a repeatable line count, so that I can verify a test fixture. | Must | G1 |

## 6. Functional requirements

### 6.1 Count and report

| ID | Requirement | Priority | Traces to | Verification |
|---|---|---|---|---|
| FR1 | WHEN the developer supplies a readable UTF-8 text file, the Line Count SHALL print its line count followed by one newline to standard output. | Must | US1 | Test |
| FR2 | IF the path is missing or the file cannot be read as UTF-8, THEN the Line Count SHALL signal failure with a nonzero exit status. | Must | US1 | Test |
| FR3 | IF the path is missing or the file cannot be read as UTF-8, THEN the Line Count SHALL describe the error on standard error. | Must | US1 | Test |

## 7. Non-functional requirements

| ID | Category | Requirement | Priority | Traces to | Verification |
|---|---|---|---|---|---|
| NFR1 | Portability | The Line Count SHALL run with 0 third-party Python packages. | Must | G1 | Inspection |

## 8. User interaction and design

The developer passes one file path to the command and reads the count from standard output. The contract defines a blank line as one line and includes a final line without a terminating newline. An empty file has zero lines.

## 9. Assumptions, constraints, and dependencies

### 9.1 Assumptions

| ID | Assumption | If it is wrong |
|---|---|---|
| A1 | The fixtures use UTF-8. | Revisit FR1 through FR3 if additional encodings are needed. |

### 9.2 Constraints

- Run on the developer's machine without network access, per the brief.

### 9.3 Dependencies

| Dependency | What the product needs from it | Owner |
|---|---|---|
| Python | Decode the file and run the command. | Project maintainer |

## 10. Open questions

| ID | Question | Blocks | Owner | Needed by |
|---|---|---|---|---|
| Q1 | Should a later phase support multiple files? | - | Product owner | Next roadmap review |

## 11. Glossary

| Term | Definition |
|---|---|
| Line Count | The local command described in this document. |
| UTF-8 | Unicode Transformation Format using 8-bit code units. |
