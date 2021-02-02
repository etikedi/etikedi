# Aergia Frontend

## Tech Stack

- `Svelte 3` Web-Framework
- `typescript` we use typings
- `rollup` Bundler
- `tinro` SPA Router
- `axios` For API Calls
- `jwt-decode` JWT lib for decoding the auth jwt.
- `dompurify` Sanitize html to be injected
- `@beyonk/svelte-notifications` Notifications for the users
- `change-case` Changing case for selects
- `chart.js` Graphs
- `chartkick` Graphs
- `copy-to-clipboard` Clipboard lib

## New to [Svelte](https://svelte.dev/)?

If you have not worked with Svelte, you will like it.
Just take the [official tutorial](https://svelte.dev/tutorial/basics), it's amazing, short and well written.

## Structure

Not all the files are included below, just the important ones to understand the structure.
Generally we organize by routes. And whitin those routes we use `views` and `component` folders for the scopes of that route. This keeps code as local as possible while still be organized.

```
.
├── public
│   ├── global.css                  # Global styles
│   └── index.html                  # HTML
├── src
│   ├── components
│   │   ├── Login.svelte
│   │   └── Nav.svelte
│   ├── lib                         # Library for utility code
│   │   ├── human.ts
│   │   └── utils.ts
│   ├── store                       # Data stores that communicate with the API
│   │   ├── auth.ts
│   │   ├── datasets.ts
│   │   ├── me.ts
│   │   └── users.ts
│   ├── ui                          # General UI Components
│   │   ├── Button.svelte
│   │   ├── Card.svelte
│   │   ├── Checkbox.svelte
│   │   └── *
│   ├── views
│   │   ├── app
│   │   │   ├── components
│   │   │   │   └── *
│   │   │   ├── users
│   │   │   │   ├── components
│   │   │   │   ├── views
│   │   │   │   └── Users.svelte
│   │   │   ├── views
│   │   │   │   └── *
│   │   │   └── App.svelte
│   │   ├── About.svelte
│   │   └── Home.svelte
│   ├── App.svelte                          # Top level App
│   └── main.ts                             # Main entry point for the app
├── rollup.config.js                        # Bundler config
└── tsconfig.json                           # Typescript config
```

## Data Stores

Data stores are handled by the native svelte stores.
The basic concept is to expose a `data` store and add `acions` as functions that write to that store.
