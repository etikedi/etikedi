# Frontend

You need the following software preinstalled: [yarn](https://yarnpkg.com/).

To install everything:

```
yarn install
```

To start the frontend (if the source code is changed the webpage will automatically reload):

```
yarn serve
```

To produce a production ready build:
```
yarn build
```

## Vue.js
The frontend is written in [Vue.js](https://vuejs.org/v2/guide/) and Javascript.
The frontend is divided into multiple components, which can be reused in many ways.
The main entrypoints to the code are `App.vue` and `main.js`, which define global stuff like color variables or the default components.
Take a look at the Vue.js guide first to have a basic understanding how the framework works, the documentation is really well written!

## Components
A Vue.js component contains a piece of HTML Template code, followed by some Javascript logic, and ended by some CSS for styling.
All of this is stored in the same single `.vue` file.
Components can include other components, so always try to make them as reusable as possible.

## API
The displayed data is retrieved over the REST Api from the backend using [axios](https://github.com/axios/axios).
The API can be accessed via so-called service files which define functions, f.e. `api/CV_Service.js`.
Note that the function needed here also needs to be existent in the backend.

## Vue state
An important piece of the frontend is state management.
For that [vuex](https://vuex.vuejs.org/) is being used.
The state is in the `store/` folder and contains of actions, getters, mutations and the state itself in the index file.

The actions can be called from the Vue components, and can change via mutations the state, which then changes and gets rendered in the Vue components.

## Bulma and Buefy
To make everything look fancy the CSS framework [Bulma](https://bulma.io/) is being used.
There exists a Vue.js integration called [Buefy](https://buefy.org/), sometimes it helps to take a look into both documentations.
For things like buttons, tooltips, etc. this should be used.
