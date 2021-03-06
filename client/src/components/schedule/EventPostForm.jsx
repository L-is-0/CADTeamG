import React from 'react';
import { connect } from 'react-redux';
import { Button, Form, Header } from 'semantic-ui-react';
import { TimeInput } from 'semantic-ui-calendar-react';
import { postEvent } from '../../redux/actions/event';

class EventPostForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      title: '',
      location: '',
      endtime: '',
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSave = this.handleSave.bind(this);
    this.handleTimeChange = this.handleTimeChange.bind(this);
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }


  handleTimeChange(event, { name, value }) {
    this.setState({ [name]: value });
  }

  async handleSave() {
    const starttime = new Date(this.props.date);
    const endtime = this.state.endtime ? new Date(`${new Date(this.props.date).toDateString()} ${this.state.endtime}`) : '';
    const event = { title: this.state.title, location: this.state.location, starttime, endtime };

    const { payload: { id } } = await this.props.postEvent(event);
    if (id) this.props.closeModal();
  }

  render() {
    const { title, location, endtime } = this.state;
    const { date, loader } = this.props;

    return (
      <Form>
        <Header block textAlign="center">Create Event on {new Date(date).toUTCString()}</Header>
        <Form.Input
          fluid
          name="title"
          iconPosition="left"
          icon="calendar outline"
          placeholder="Enter title"
          type="text"
          onChange={this.handleChange}
          value={title}
        />
        <br />
        <Form.Input
          fluid
          name="location"
          iconPosition="left"
          icon="building outline"
          placeholder="Enter location"
          type="text"
          onChange={this.handleChange}
          value={location}
        />
        <br />
        <TimeInput
          fluid
          closable
          autoComplete="off"
          hideMobileKeyboard
          name="endtime"
          iconPosition="left"
          placeholder="Enter end time"
          type="text"
          onChange={this.handleTimeChange}
          value={endtime}
        />
        <br />
        <Button
          onClick={this.handleSave}
          fluid
          loading={loader.POST_EVENT}
        >
          Save
        </Button>
      </Form>
    );
  }
}

const mapStateToProps = (state) => {
  const { loader } = state;
  return { loader };
};

export default connect(mapStateToProps, { postEvent })(EventPostForm);
