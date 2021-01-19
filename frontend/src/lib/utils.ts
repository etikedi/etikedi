// @ts-ignore
export const isDev: boolean = __dev__ // Replaced by Rollup

console.log('Dev', isDev)

export function devProdSwitch<A = any, B = any>(dev: A, prod: B): A | B {
  return isDev ? dev : prod
}
