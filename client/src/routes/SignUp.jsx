import React from 'react';
import { connect } from 'react-redux';
import {
  Button, Input, Segment, Message,
} from 'semantic-ui-react';
import Layout from '../components/Layout';
import { signUp, clearErrors } from '../redux/actions';

class SignUp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      password2: '',
    };
    this.props.clearErrors();
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }

  async handleSubmit() {
    const { username, password, password2 } = this.state;

    const { payload } = await this.props.signUp({ username, password, password2 });
    console.log(payload);

    this.setState({ username: '', password: '', password2: '' });
  }

  render() {
    const { username, password, password2 } = this.state;
    const { loaders, errors } = this.props;

    return (
      <Layout>
        <Segment placeholder>
          <Input
            name="username"
            icon="user"
            iconPosition="left"
            placeholder="Username"
            onChange={this.handleChange}
            value={username}
          />
          <br />
          <Input
            name="password"
            icon="lock"
            iconPosition="left"
            placeholder="Password"
            type="password"
            onChange={this.handleChange}
            value={password}
          />
          <br />
          <Input
            name="password2"
            icon="lock"
            iconPosition="left"
            placeholder="Repeat Password"
            type="password"
            onChange={this.handleChange}
            value={password2}
          />
          <br />
          <Button
            loading={loaders.SIGN_UP}
            onClick={this.handleSubmit}
            fluid
          >
            Sign Up
          </Button>
          {Object.keys(errors).length > 0 ? (
            <Message
              compact
              error
              header="Error"
              list={Object.values(errors).map((error) => <p key={error}>{error}</p>)}
            />
          ) : <></>}
        </Segment>
      </Layout>
    );
  }
}

const mapStateToProps = (state) => {
  const { loaders, errors } = state;
  return { loaders, errors };
};


export default connect(mapStateToProps, { signUp, clearErrors })(SignUp);