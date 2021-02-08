# Etikedi

Open-source active-learning backed multipurpose labeling tool.
Inspired by [prodigy](https://prodi.gy/demo) and [Labelbox](https://labelbox.com/).

## Installation

`Note` after cloning this repo you first need to initialize the git submodules, which you can in laymen terms think of as including the active learning code from a different git repository.

```bash
# Git
git submodule init
git submodule update

# Frontend
cd frontend
npm i
```

## Developing

We use docker for the backend.
Both backend and frontend have hot reloading out of the box.

1. Backend: `docker-compose up --build`.
2. Frontend: `cd frontend` then `npm run dev`

For further information check the related `README.md` in the `./frontend` and `./backend` directory.
