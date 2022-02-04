import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'vector',
})
export class VectorPipe implements PipeTransform {
  transform(value: number[], ...args: unknown[]): unknown {
    let s = '';
    for (let i = 0; i < value.length; i++) {
      if (value[i] == 0) {
        continue;
      }
      if (value[i] < 0) {
        s += ' - ';
      } else {
        s += ' + ';
      }
      s += Math.abs(value[i]) == 1 ? '' : Math.abs(value[i]);
      s += `x${i + 1}`;
    }
    if (s[1] == '+') {
      s = s.substring(3);
    } else {
      s = s.substring(3);
      s = '-' + s;
    }
    return s;
  }
}
