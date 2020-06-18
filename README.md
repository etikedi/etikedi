# AERGIA
`Note` after cloning this repo you first need to initialize the git submodules, which you can in laymen terms think of as including the active learning code from a different git repository.

```
git submodule init
git submodule update
```

Open-source active-learning backed multipurpose labeling tool.
Inspired by [prodigy](https://prodi.gy/demo) and [Labelobx](https://labelbox.com/).

Photo by [Holger Link](https://unsplash.com/@photoholgic) on [Unsplash](https://unsplash.com/).

## One-liner to start app:
```pipenv run env FLASK_APP=aergia.py FLASK_ENV=development flask run```
