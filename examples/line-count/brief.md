# Line Count brief

Build a local Python command that reports the number of lines in a UTF-8 text file. An empty file has zero lines. Count blank lines and a final line without a newline. The command takes one path and prints only the count and a terminating newline on success. If the argument is missing or the file cannot be read or decoded, report the problem on standard error and exit with a nonzero code. The application serves a developer checking fixtures. This phase excludes standard input, multiple paths, and recursive counting.

Use the Python standard library. The first phase delivers this single command and uses `python3 -m compileall -q line_count.py tests` and `python3 -m unittest discover -s tests` as the project gates. The public test seam is the command's exit status, standard output, and standard error.
