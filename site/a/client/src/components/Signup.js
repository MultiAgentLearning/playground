/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { connect } from 'react-redux';
import { userActions } from '../actions';
import { history } from '../utils';
import GithubOAuth from './GithubOAuth'
import HeaderStationary from './HeaderStationary'
import { validateEmail } from '../utils/misc'
import {
  Container,
  Divider,
  Form,
  Grid,
  Message,
  Segment
} from 'semantic-ui-react'


class Signup extends Component {
  constructor(props) {
    super(props);
    
    this.state = {
      name: '',
      email: '',
      password: '',
      repeat: '',
      signupError: false,
      signupErrorMessage: '',
      submitted: false,
      loaded: false
    };
    
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    this.checkForUser(this.props);    
  }

  checkForUser(props) {
    if (props.loggedIn) {
      history.push('/')
    } else {
      this.setState({loaded: true});
    }
  }

  componentWillReceiveProps(props) {
    if (props.error && props.error !== '') {
      this.setState({signupError: true, signupErrorMessage: props.error});
    }
  }

  handleChange(e) {
    const { name, value } = e.target;
    this.setState({
      [name]: value,
      signupError: false,
      signupErrorMessage: '',
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    
    this.setState({ submitted: true });
    const { name, email, password, repeat } = this.state;
    const { dispatch } = this.props;

    var signupError = false;
    var signupErrorMessage = '';
    if (name === '') {
      signupError = true;
      signupErrorMessage = 'Please enter a name.';
    } else if (email === '') {
      signupError = true;
      signupErrorMessage = 'Please enter an email.';
    } else if (password === '') {
      signupError = true;
      signupErrorMessage = 'Please enter a password.';
    } else if (!validateEmail(email)) {
      signupError = true;
      signupErrorMessage = 'Please enter a valid email.';
    } else if (repeat !== password) {
      signupError = true;
      signupErrorMessage = 'Please enter your password again to verify.';
    }

    if (!signupError) {
      dispatch(userActions.register(name, email, password));
    }
    this.setState({signupError: signupError, signupErrorMessage: signupErrorMessage})
  }

  renderSignupForm() {
    const { name, email, password, repeat, signupError, signupErrorMessage } = this.state

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
            <Form size='large' error={signupError} onSubmit={this.handleSubmit}>
              <Segment stacked>
                <Form.Input
                  fluid
                  icon='user'
                  iconPosition='left'
                  placeholder='Name'
                  name='name'
                  value={name}
                  onChange={this.handleChange}
                />
                <Form.Input
                  fluid
                  icon='user'
                  iconPosition='left'
                  placeholder='Email'
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
                <Form.Input
                  fluid
                  icon='lock'
                  iconPosition='left'
                  placeholder='Repeat Password'
                  type='password'
                  name='repeat'
                  value={repeat}
                  onChange={this.handleChange}
                />
                
                <Form.Button color='teal' fluid size='large'>Signup</Form.Button>
                <Message
                  error
                  header='Slight mishap perhaps?'
                  content={signupErrorMessage}
                />
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
              Already joined? <a href='/login'>Login</a>
            </Message>
          </Grid.Column>
        </Grid>
      </div>
    );
  }

  render() {
    const { loaded } = this.state;

    return (
      <div>
        <Segment
          textAlign='center'
          style={{ minHeight: 700, padding: '1em 0em' }}
          vertical
        > 
          <Container>
            <HeaderStationary active="signup" />
          </Container>
          {!this.state.loaded ? null : this.renderSignupForm()}
        </Segment> 
      </div>
    );
  }
}

function mapStateToProps(state) {
  const { registering, error } = state.registration;
  const { loggedIn, user } = state.authentication;
  return {
    registering,
    error,
    loggedIn,
    user
  };
}

const connectedSignup = connect(mapStateToProps)(Signup);
export { connectedSignup as Signup };
