// Shamelessly copied from: https://stackoverflow.com/questions/45194598/using-process-env-in-typescript/53981706#53981706
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      PRODUCTION_URL?: string;
    }
  }
}

// If this file has no import/export statements (i.e. is a script)
// convert it into a module by adding an empty export statement.
export {}