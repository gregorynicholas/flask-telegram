#!/bin/sh

cd ./docs
make html

git checkout gh-pages

cp -rf ./_build/html/* ../

cd ../
git add *.html searchindex.js objects.inv .buildinfo _static/ _sources/
git commit -m "updated docs html build."
git pull origin gh-pages
git push origin gh-pages

git checkout -f master
