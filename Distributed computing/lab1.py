import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

STATE_STANDING = "STATE_STANDING"
STATE_CASTING = "STATE_CASTING"
STATE_WAITING = "STATE_WAITING"
STATE_BITE = "STATE_BITE"
STATE_FIGHTING = "STATE_FIGHTING"
STATE_CATCHING = "STATE_CATCHING"
STATE_VICTORY = "STATE_VICTORY"


class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class StateStanding(State):
    async def run(self):
        print("I'm standing at the lake")
        msg = Message(to=str(self.agent.jid))
        msg.body = "msg_from_state_one_to_state_three"
        await self.send(msg)
        self.set_next_state(STATE_CASTING)


class StateCasting(State):
    async def run(self):
        print("Casting out the lure")
        self.set_next_state(STATE_WAITING)


class StateWaiting(State):
    async def run(self):
        print("I'm waiting for a fish to bite")
        msg = await self.receive(timeout=5)
        print(f"State Three received message {msg.body}")
        # no final state is setted, since this is a final state
        self.set_next_state(STATE_BITE)

class StateBite(State):
    async def run(self):
        print("Insanely huge fish bites")
        self.set_next_state(STATE_FIGHTING)

class StateFighting(State):
    async def run(self):
        print("incredible fight against 10 kg pike")
        self.set_next_state(STATE_CATCHING)

class StateCatching(State):
    async def run(self):
        print("Catch personal best pike and cries a little")
        self.set_next_state(STATE_VICTORY)

class StateVictory(State):
    async def run(self):
        print("Celebrates catching the fish of a lifetime with a cold beer")

class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_STANDING, state=StateStanding(), initial=True)
        fsm.add_state(name=STATE_CASTING, state=StateCasting())
        fsm.add_state(name=STATE_WAITING, state=StateWaiting())
        fsm.add_state(name=STATE_BITE, state=StateBite())
        fsm.add_state(name=STATE_FIGHTING, state=StateFighting())
        fsm.add_state(name=STATE_CATCHING, state=StateCatching())
        fsm.add_state(name=STATE_VICTORY, state=StateVictory())
        fsm.add_transition(source=STATE_STANDING, dest=STATE_CASTING)
        fsm.add_transition(source=STATE_CASTING, dest=STATE_WAITING)
        fsm.add_transition(source=STATE_WAITING, dest=STATE_BITE)
        fsm.add_transition(source=STATE_BITE, dest=STATE_FIGHTING)
        fsm.add_transition(source=STATE_FIGHTING, dest=STATE_CATCHING)
        fsm.add_transition(source=STATE_CATCHING, dest=STATE_VICTORY)
        self.add_behaviour(fsm)


async def main():
    fsmagent = FSMAgent("h23davsk@jabbers.one/pidgin", "Kaffesump")
    await fsmagent.start()

    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())