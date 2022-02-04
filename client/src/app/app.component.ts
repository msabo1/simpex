import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { DetailsComponent } from './details/details.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  history: any;
  mode: string = 'text';
  textForm: FormGroup = new FormGroup({
    func: new FormControl(null, Validators.required),
    goal: new FormControl(null, Validators.required),
    conditions: new FormControl(null, Validators.required),
    strategy: new FormControl(null, Validators.required),
  });

  matrixForm: FormGroup = new FormGroup({
    c: new FormControl(null, Validators.required),
    goal: new FormControl('min', Validators.required),
    A: new FormControl(null, Validators.required),
    b: new FormControl(null, Validators.required),
    strategy: new FormControl(null, Validators.required),
  });

  result: any;
  constructor(
    private readonly matDialog: MatDialog,
    private readonly http: HttpClient
  ) {}

  ngOnInit() {
    this.history = JSON.parse(localStorage.getItem('history') || '[]');
    if (this.history.length == 0) {
      this.history = [
        {
          func: '-x1 - 2x2',
          goal: 'min',
          conditions:
            '-x1 - x2 + x3 = -5\nx1 + x2 + x4 = 8\nx1 + x5 = 6\nx2 + x6 = 6\nx1, x2, x3, x4, x5, x6 >= 0',
          strategy: 'bland',
          mode: 'text',
        },
        {
          c: '-1 -2 0 0 0 0',
          goal: 'min',
          A: '-1 -1 1 0 0 0\n1 1 0 1 0 0\n1 0 0 0 1 0\n0 1 0 0 0 1',
          b: '-5 8 6 6',
          strategy: 'lex',
          mode: 'matrix',
        },
      ];
    }
  }

  openDetails() {
    this.matDialog.open(DetailsComponent, {
      data: this.result,
    });
  }

  setState(state: any) {
    this.mode = state.mode;
    state = { ...state };
    delete state.mode;
    if (this.mode === 'text') {
      this.textForm.setValue(state);
    } else {
      this.matrixForm.setValue(state);
    }
    // this.textForm.controls['func'].setValue(state.func);
    // this.textForm.controls['goal'].setValue(state.goal);
    // this.textForm.controls['conditions'].setValue(state.conditions);
    // this.textForm.controls['strategy'].setValue(state.strategy);
  }

  setMode(mode: string) {
    this.mode = mode;
  }

  solve() {
    let req =
      this.mode === 'text' ? this.textForm.value : this.matrixForm.value;
    req = { ...req, mode: this.mode };
    this.history.unshift(req);
    this.history.splice(10);
    localStorage.setItem('history', JSON.stringify(this.history));
    console.log(req);
    this.http.post('/api/solve', req).subscribe((result) => {
      // @ts-ignore
      if (result.status == 4) {
        this.result = result;
        return;
      }
      // @ts-ignore
      result = {
        ...result,
        // @ts-ignore
        realBase: new Array(result.table[0].length - 1).fill(0),
      };
      let j = 0;
      // @ts-ignore
      for (let i = 1; i < result.table.length; i++) {
        // @ts-ignore
        result.realBase[result.base[i - 1]] = result.table[i][0];
      }
      console.log(result);
      this.result = result;
    });
  }

  onFieldChange() {
    this.result = null;
  }
}
