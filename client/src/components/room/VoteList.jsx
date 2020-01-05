import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Grid, Header, Card, Button } from 'semantic-ui-react';
import { ioVote } from '../../redux/actions/socket';

const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

class VoteList extends Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(timeslot) {

    this.props.ioVote(this.props.socket, timeslot.target.value)

  }


  render() {
    const { session } = this.props;

    const dates = Object.keys(session.timeslots).reduce((acc, e) => acc.set(days[new Date(e).getDay()], [...(days[acc.get(new Date(e).getDay())] || []), e]), new Map());

    return (    
      <Grid columns={dates.size || 7} stackable>
        {[...dates.entries()].map((e) => {

          const [day, slots] = e;

          return (

          <Grid.Column key={slots} >

            <Header as="h3" textAlign="center" dividing>
              {day}
            </Header>

            {slots.map((slot) => {
              
              const numberOfVotes = session.timeslots[slot].length;

              return (
                <Card key={slot} fluid centered>
                  <Card.Content>
    
                    <Card.Header>
                      {new Date(e[1]).toUTCString()}
                    </Card.Header>
    
                    <Card.Description>
                      {numberOfVotes}
                    </Card.Description>
    
                  </Card.Content>
    
                  <Card.Content extra>
                    <Button
                      primary
                      onClick={this.handleClick}
                      fluid
                      value={slot}
                    >
                      Vote
                    </Button>
                  </Card.Content>
    
                </Card>
              );

            })}

          </Grid.Column>

        )})}
      </Grid>
    );
  }
}

const mapStateToProps = (state) => {
  const { session } = state;
  return { session };
};

export default connect(mapStateToProps, { ioVote })(VoteList);