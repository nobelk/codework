#!/bin/sh
# Create a diverged feature branch and a bare remote under an empty directory.
set -eu

sandbox=$(cd "$1" && pwd)
git init -q --bare --initial-branch=main "$sandbox/remote.git"
git init -q --initial-branch=main "$sandbox/work"
cd "$sandbox/work"
git config user.name "Codework Fixture"
git config user.email "codework@example.invalid"
git config core.autocrlf false
git config rerere.enabled false

printf 'printf "mode=legacy\\n"\n' > render.sh
printf 'original\n' > notes.txt
printf 'cache.local\ncollision-file\ncollision-directory\n' > .gitignore
cat > verify.sh <<'GATE'
#!/bin/sh
set -eu
actual=$(sh render.sh)
if test -f feature.md; then
    expected=$(cat feature.md)
    test "$actual" = "$expected"
fi
GATE
git add -- .gitignore render.sh notes.txt verify.sh
git commit -qm "Start the command fixture"
git remote add origin "$sandbox/remote.git"
git switch -qc feature
printf 'printf "mode=feature\\n"\n' > render.sh
printf 'mode=feature\n' > feature.md
git add -- render.sh feature.md
git commit -qm "Add feature mode"
git push -qu origin feature

git switch -q main
printf 'printf "mode=main\\n"\n' > render.sh
printf 'The first mode is main. Branch modes may follow it, separated by a comma.\n' > README.md
git add -- render.sh README.md
git commit -qm "Set the default mode and document combined modes"
git push -qu origin main

git switch -q feature
printf 'staged\n' >> notes.txt
git add -- notes.txt
printf 'unstaged\n' >> notes.txt
printf 'untracked\n' > scratch.txt
printf 'ignored\n' > cache.local
printf '%s\n' "$sandbox/work"
