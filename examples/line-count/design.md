# Line Count design

| | |
|---|---|
| **Status** | Example |
| **Date** | 2026-11-21 |
| **Scope** | Count one local file |
| **Sources** | [PRD](prod_req.md) |

## 1. Introduction and overview

A developer gives Line Count one file path and reads the count on standard output. The command runs as a single process and reports failure on standard error.

| Requirements | Design | Task | Check |
|---|---|---|---|
| FR1 | Sections 2 and 4 | Count a local file | Assert counts for empty, blank, and unterminated lines |
| FR2, FR3 | Sections 4 and 6 | Report invalid input | Assert error stream and nonzero exit status |
| NFR1 | Section 7 and [ADR 1](adr-0001.md) | Keep the command standalone | Run with standard-library Python |

## 2. System architecture

### 2.1 Architecture pattern

The single-process command uses a thin argument boundary and streams the file through standard-library text iteration.

### 2.2 System context

Figure 1 shows the developer, command, and local file system.

```mermaid
flowchart LR
    developer["Developer (Person)"] -->|"Supplies a path and reads the result"| command["Line Count (Software System)"]
    command -->|"Reads file bytes"| disk["Local file system (External System)"]
```
*Figure 1. Line Count system context.*

### 2.3 Container

Figure 2 shows the only container, the Python process.

```mermaid
flowchart LR
    developer["Developer (Person)"] -->|"Invokes the command"| process["Command process (Container, Python)"]
    process -->|"Reads a local file"| disk["Local file system (External System)"]
```
*Figure 2. Line Count container.*

## 3. Data design

The application owns no persistent data. It reads Unicode text sequentially and keeps only the current count and line in memory.

## 4. Interface design

| Interface | Contract | Failure |
|---|---|---|
| Developer to Line Count | `python3 line_count.py path` prints one integer and a newline | Diagnostic on standard error and nonzero exit status |
| Line Count to local file system | Read-only UTF-8 text selected by the supplied path | Missing, unreadable, or undecodable file produces a diagnostic |

## 5. Component design

The command boundary validates the argument and formats the result. File iteration counts each line yielded by the text reader.

## 6. User interface design

The developer runs one command in a shell. Successful runs return a count, including zero for an empty file. Failed runs return a diagnostic and no count.

## 7. Assumptions and dependencies

The project uses the Python runtime and local file system. The package uses the standard library. The input is UTF-8 and the supported size follows the operating system's file limits.

## 8. Glossary of terms

| Term | Definition |
|---|---|
| ADR | Architecture decision record. |
| Container | A separately running unit in the diagram. Here it is the Python process. |
| FR1 | Line count requirement. |
| FR2 | Failure exit status requirement. |
| FR3 | Error diagnostic requirement. |
| Line Count | The command described here. |
| NFR1 | Non-functional requirement identifier. |
| PRD | Product requirements document. |
| UTF-8 | Unicode Transformation Format using 8-bit code units. |
