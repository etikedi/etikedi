// @ts-ignore
export const isDev: boolean = __dev__ // Replaced by Rollup

export function devProdSwitch<A = any, B = any>(dev: A, prod: B): A | B {
  return isDev ? dev : prod
}
