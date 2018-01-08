/** jsx React.DOM */
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux'
import { Store } from './reducers/store';
import './index.css';
import 'semantic-ui-css/semantic.min.css';
import { App } from './App';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
  <Provider store={Store}>
    <App />
  </Provider>,
  document.getElementById('root')
);
registerServiceWorker();
