import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatStepper } from '@angular/material/stepper';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css'],
})
export class DetailsComponent implements OnInit {
  @ViewChild('container') container;
  @ViewChild(MatStepper) stepper: MatStepper;

  storyStep = 2;
  step = 0;
  last = false;
  phase = 0;
  constructor(@Inject(MAT_DIALOG_DATA) public readonly result) {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    this.container.nativeElement.style['min-width'] =
      this.container.nativeElement.clientWidth + 'px';
    if (this.result.mode == 'matrix') {
      this.storyStep = 1;
    } else {
      this.storyStep = 0;
    }
  }

  getInfluences() {
    return this.result.tables[this.phase][this.step][0].filter(
      (item, i) => i !== 0
    );
  }

  getTableWithoutFirstRow() {
    return this.result.tables[this.phase][this.step].filter(
      (item, i) => i !== 0
    );
  }

  getARow(row) {
    return row.filter((item, i) => i !== 0);
  }

  nextStep() {
    if (this.storyStep == 0) {
      this.storyStep++;
      return;
    }
    if (this.storyStep == 1) {
      this.storyStep++;
      return;
    }
    if (this.storyStep == 2) {
      if (this.step + 1 == this.result.tables[this.phase].length - 1) {
        this.last = true;
      }
      if (this.step + 1 == this.result.tables[this.phase].length) {
        this.phase = 1;
        this.step = 0;
        this.last =
          this.step == this.result.tables[this.phase].length - 1 ? true : false;
        this.storyStep++;
        return;
      }
      this.step++;
    }
    if (this.storyStep == 3) {
      if (this.step + 1 == this.result.tables[this.phase].length - 1) {
        this.last = true;
      }
      this.step++;
    }
  }

  prevStep() {
    if (this.storyStep == 3) {
      if (this.step == 0) {
        this.phase = 0;
        this.step = this.result.tables[this.phase].length - 1;
        this.last = true;
        this.storyStep--;
        return;
      } else {
        this.last = false;
        this.step--;
        return;
      }
    }

    if (this.storyStep == 2) {
      if (this.step == 0) {
        this.storyStep--;
        return;
      } else {
        this.last = false;
        this.step--;
        return;
      }
    }

    if (this.storyStep == 1) {
      if (this.result.mode == 'text') {
        this.storyStep--;
        return;
      }
    }
  }
}
