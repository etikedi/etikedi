# Etikedi

Open-source active-learning backend multipurpose labeling tool.
Inspired by [prodigy](https://prodi.gy/demo) and [Labelbox](https://labelbox.com/).

## Battle mode
Compare two active learning strategies (implemented by [alipy](https://github.com/NUAA-AL/ALiPy)) and visualize ([altair](https://github.com/altair-viz/altair)) the
learning process with numerous charts. The strategies are highly configurable and can be combined with multiple sklearn al-model.
More information can be found [here](backend/battle_mode/Readme.md) and [here](https://ecir2022.org/uploads/460.pdf).

## Installation

After cloning this repo you first need to initialize the git submodules, which you can in laymen terms think of as including the active learning code from a different git repository.

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
