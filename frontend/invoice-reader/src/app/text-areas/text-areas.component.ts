import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl } from '@angular/forms';

@Component({
  selector: 'app-text-areas',
  templateUrl: './text-areas.component.html',
  styleUrls: ['./text-areas.component.scss']
})
export class TextAreasComponent implements OnInit {
  textAreas: { content: string; type: string }[] = [];
  textAreasForm!: FormGroup;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.textAreasForm = this.formBuilder.group({});
  }

  addTextArea(content: string, type: string) {
    this.textAreas.push({ content, type });

    const controlName = this.generateControlName();
    this.textAreasForm.addControl(controlName, new FormControl(content));
  }

  generateControlName() {
    return `textArea_${this.textAreas.length}`;
  }
}
