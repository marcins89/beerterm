import { Component } from '@angular/core';
import {Observable} from 'rxjs/Observable';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  title = 'app works!';
  private websocket;
  
  constructor() {
  	this.websocket = new WebSocket("ws://" + window.location.hostname + ":81");
  	this.websocket.onopen =  (evt) => {
  		console.log("onopen");
		console.log(evt);
    };
  	this.websocket.onmessage = (evt) => { 
        console.log(evt);
        this.title = evt.data;
    };
  }
}
