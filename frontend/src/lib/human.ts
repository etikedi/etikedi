// FROM HERE:
// https://github.com/cerberus-ab/human-readable-numbers/blob/master/src/index.js

const PREFIXES = {
  '24': 'Y',
  '21': 'Z',
  '18': 'E',
  '15': 'P',
  '12': 'T',
  '9': 'G',
  '6': 'M',
  '3': 'k',
  '0': '',
  '-3': 'm',
  '-6': 'µ',
  '-9': 'n',
  '-12': 'p',
  '-15': 'f',
  '-18': 'a',
  '-21': 'z',
  '-24': 'y',
}

function getExponent(n: number) {
  if (n === 0) {
    return 0
  }
  return Math.floor(Math.log10(Math.abs(n)))
}

function precise(n: number) {
  return Number.parseFloat(n.toPrecision(3))
}

export function humanize(sn: string) {
  var n = precise(Number.parseFloat(sn))
  var e = Math.max(Math.min(3 * Math.floor(getExponent(n) / 3), 24), -24)
  return precise(n / Math.pow(10, e)).toString() + PREFIXES[e]
}
