import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
import random
import asyncio
from spade.message import Message

STATE_STANDING = "STATE_STANDING"
STATE_CASTING = "STATE_CASTING"
STATE_WAITING = "STATE_WAITING"
STATE_BITE = "STATE_BITE"
STATE_FIGHTING = "STATE_FIGHTING"
STATE_CATCHING = "STATE_CATCHING"
STATE_LOST = "STATE_LOST"
STATE_VICTORY = "STATE_VICTORY"
STATE_DEFEAT = "STATE_DEFEAT"
STATE_TREE = "STATE_TREE"
STATE_ENDING = "STATE_ENDING"


class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


class StateStanding(State):
    async def run(self):
        print("I'm standing at the lake on a beautiful day")
        await asyncio.sleep(5)
        print("do you wan to fish? yes or no")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_CASTING)
        elif userinput == "no":
            print("Goes home for today and returns the next day")
            self.set_next_state(STATE_STANDING)


class StateCasting(State):
    async def run(self):
        print("Casting out the lure")
        await asyncio.sleep(5)
        randomnumber = random.random()
        if randomnumber < 0.1:
            print("you casted in to a tree and the lure was lost")
            self.set_next_state(STATE_TREE)
        else:
            self.set_next_state(STATE_WAITING)

class StateTree(State):
    async def run(self):
        print("do you want to put on a new lure and trying again? yes or no")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_CASTING)
        elif userinput == "no":
            self.set_next_state(STATE_DEFEAT)



class StateWaiting(State):
    async def run(self):
        print("I'm waiting for a fish to bite")
        await asyncio.sleep(5)
        self.set_next_state(STATE_BITE)

class StateBite(State):
    async def run(self):
        print("Insanely huge fish bites")
        await asyncio.sleep(5)
        self.set_next_state(STATE_FIGHTING)

class StateFighting(State):
    async def run(self):
        print("incredible fight against 10 kg pike")
        await asyncio.sleep(5)
        randomnumber = random.random()
        # vi använder random module för att slumpa ett tal mellan 0-1. Detta är för att skapa
        # ett event av ovisshet för fiskaren, precis som i riktiga livet.
        if randomnumber > 0.5:
            print("You have managed to make the fish tired, keep fighting!")
            await asyncio.sleep(5)
            self.set_next_state(STATE_CATCHING)
        else:
            print("The fish is too strong! It starts to slip..")
            await asyncio.sleep(5)
            self.set_next_state(STATE_LOST)


class StateLost(State):
    async def run(self):
        print("The fish was lost")
        await asyncio.sleep(5)
        print("feeling like the worst fisherman in history")
        self.set_next_state(STATE_DEFEAT)


class StateCatching(State):
    async def run(self):
        print("Catch personal best pike and cries a little")
        await asyncio.sleep(5)
        self.set_next_state(STATE_VICTORY)

class StateVictory(State):
    async def run(self):
        print("Celebrates catching the fish of a lifetime with a cold beer")
        await asyncio.sleep(5)

class StateDefeat(State):
    async def run(self):
        await asyncio.sleep(5)
        print("you full of sadness and thoughts of selling your'e fishing gear enters your mind")
        await asyncio.sleep(5)
        print("you leave the lake as a broken man")

class StateEnding(State):
    async def run(self):
        print("Celebrates catching the fish of a lifetime with a cold beer")
        await asyncio.sleep(5)


class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_STANDING, state=StateStanding(), initial=True)
        fsm.add_state(name=STATE_CASTING, state=StateCasting())
        fsm.add_state(name=STATE_TREE, state=StateTree())
        fsm.add_state(name=STATE_WAITING, state=StateWaiting())
        fsm.add_state(name=STATE_BITE, state=StateBite())
        fsm.add_state(name=STATE_FIGHTING, state=StateFighting())
        fsm.add_state(name=STATE_CATCHING, state=StateCatching())
        fsm.add_state(name=STATE_VICTORY, state=StateVictory())
        fsm.add_state(name=STATE_LOST, state=StateLost())
        fsm.add_state(name=STATE_DEFEAT, state=StateDefeat())
        fsm.add_state(name=STATE_ENDING, state=StateEnding())
        fsm.add_transition(source=STATE_STANDING, dest=STATE_CASTING)
        fsm.add_transition(source=STATE_STANDING, dest=STATE_STANDING)
        fsm.add_transition(source=STATE_CASTING, dest=STATE_WAITING)
        fsm.add_transition(source=STATE_CASTING, dest=STATE_TREE)
        fsm.add_transition(source=STATE_TREE, dest=STATE_CASTING)
        fsm.add_transition(source=STATE_TREE, dest=STATE_DEFEAT)
        fsm.add_transition(source=STATE_WAITING, dest=STATE_BITE)
        fsm.add_transition(source=STATE_BITE, dest=STATE_FIGHTING)
        fsm.add_transition(source=STATE_FIGHTING, dest=STATE_CATCHING)
        fsm.add_transition(source=STATE_FIGHTING, dest=STATE_LOST)
        fsm.add_transition(source=STATE_CATCHING, dest=STATE_VICTORY)
        fsm.add_transition(source=STATE_LOST, dest=STATE_DEFEAT)
        self.add_behaviour(fsm)


async def main():
    fsmagent = FSMAgent("h23patpe@conversations.im", "Jhgblo10")
    await fsmagent.start()

    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())