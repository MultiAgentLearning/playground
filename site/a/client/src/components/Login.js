/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { connect } from 'react-redux';
import { history } from '../utils';
import { userActions } from '../actions';
import GithubOAuth from './GithubOAuth'
import HeaderStationary from './HeaderStationary'
import { validateEmail } from '../utils/misc'
import {
  Container,
  Divider,
  Form,
  Grid,
  Message,
  Segment,
} from 'semantic-ui-react'


class Login extends Component {
  constructor(props) {
    super(props);

    this.state = {
      email: '',
      password: '',
      loginError: false,
      loginErrorMessage: '',
      loaded: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    this.checkForUser(this.props);    
  }

  checkForUser(props) {
    console.log('login checking')
    console.log(props);
    if (props.loggedIn) {
      console.log('CFU push');
      history.push('/')
    } else {
      console.log('CFU no');
      this.setState({loaded: true});
    }
  }

  handleChange(e) {
    const { name, value } = e.target;
    this.setState({ [name]: value, loginError: false, loginErrorMessage: '' });
  }

  handleSubmit(e) {
    e.preventDefault();
    
    const { email, password } = this.state;
    const { dispatch } = this.props;

    var loginError = false;
    var loginErrorMessage = '';
    if (email === '') {
      loginError = true;
      loginErrorMessage = 'Please enter an email.';
    } else if (password === '') {
      loginError = true;
      loginErrorMessage = 'Please enter a password.';
    } else if (!validateEmail(email)) {
      loginError = true;
      loginErrorMessage = 'Please enter a valid email.';
    }

    if (!loginError) {
      dispatch(userActions.login(email, password));
    }
    this.setState({loginError: loginError, loginErrorMessage: loginErrorMessage})
  }

  renderLoginForm() {
    const { email, password, loginError, loginErrorMessage } = this.state;

    return (
      <div className='login-form'>
        <style>{`
      body > div,
      body > div > div,
      body > div > div > div,
      body > div > div > div > div,
      body > div > div > div > div > div,
      body > div > div > div > div > div > div.login-form {
        height: 100%;
      }
    `}</style>
        <Grid
          textAlign='center'
          style={{ height: '100%' }}
          verticalAlign='middle'
        >
          <Grid.Column style={{ maxWidth: 450, marginTop: -100 }}>
            <Form size='large' error={loginError} onSubmit={this.handleSubmit}>
              <Segment stacked>
                <Form.Input
                  fluid
                  icon='user'
                  iconPosition='left'
                  placeholder='Email address'
                  name='email'
                  value={email}
                  onChange={this.handleChange}
                />
                <Form.Input
                  fluid
                  icon='lock'
                  iconPosition='left'
                  placeholder='Password'
                  type='password'
                  name='password'
                  value={password}
                  onChange={this.handleChange}
                />

                <Message
                  error
                  header='Something went wrong.'
                  content={loginErrorMessage}
                />
                <Form.Button color='teal' fluid size='large'>Login</Form.Button>
                <Divider
                  as='h4'
                  className='header'
                  horizontal
                  style={{ margin: '1.5em 0em', textTransform: 'uppercase' }}
                >
                  <a>Or</a>
                </Divider>
                <GithubOAuth />
              </Segment>
            </Form>
            <Message>
              New to us? <a href='/signup'>Sign Up</a>
            </Message>
          </Grid.Column>
        </Grid>
      </div>
    );
  }
  
  render() {
    return (
      <div>
        <Segment
          textAlign='center'
          style={{ minHeight: 700, padding: '1em 0em' }}
          vertical
        > 
          <Container>
            <HeaderStationary active="login" />
          </Container>
          {!this.state.loaded ? null : this.renderLoginForm()}
        </Segment> 
      </div>
    );
  }
}

function mapStateToProps(state) {
  const { loggedIn } = state.authentication;
  return {
    loggedIn
  };
}

const connectedLogin = connect(mapStateToProps)(Login);
export { connectedLogin as Login };

