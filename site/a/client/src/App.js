/** jsx React.DOM */
import React from 'react'
import { Component } from 'react';
import { connect } from 'react-redux';
import { history } from './utils';
import { alertActions } from './actions';

import { AuthenticatedRoute } from './components/AuthenticatedRoute';
import { WrapLoggedInCheck } from './components/WrapLoggedInCheck';
import { Home } from './components/Home';
import { Login } from './components/Login';
import { Profile } from './components/Profile';
import { Signup } from './components/Signup';

import {
  Router,
  Redirect,
  Route,
  Switch
} from 'react-router-dom'

const style = (
  <style>{`
    @keyframes back-to-docs {
        0% { transform: translateY(0); }
        50% { transform: translateY(0.35em); }
        100% { transform: translateY(0); }
    }
  `}</style>
)

// TODO: Instead of wrapping everything in WrapLoggedInCheck, put it over App.
class App extends Component {
  constructor(props) {
    super(props);

    const { dispatch } = this.props;
    history.listen((location, action) => {
      // clear alert on location change
      dispatch(alertActions.clear());
    });
  }

  render() {
    // TODO: Display the alert somewhere.
    const { alert } = this.props;

    return (
      <div>
        {style}
        <Router history={history}>
          <Switch>
            <Route exact path="/" component={WrapLoggedInCheck(Home)} />
            <Route path="/login" component={WrapLoggedInCheck(Login)} />
            <Route path="/signup" component={WrapLoggedInCheck(Signup)} />
            <AuthenticatedRoute path="/me" component={WrapLoggedInCheck(Profile)} />
            <Route path="/profile/:slug" component={WrapLoggedInCheck(Profile)} />
            <Redirect to="/" />
          </Switch>
        </Router>
      </div>
    );
  }
}

function mapStateToProps(state) {
  const { alert } = state;
  return {
    alert,
  };
}

const connectedApp = connect(mapStateToProps)(App);
export { connectedApp as App };
