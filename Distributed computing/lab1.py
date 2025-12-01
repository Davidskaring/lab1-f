from enum import nonmember

import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
import random
import asyncio
from spade.message import Message
#här deklarer vi dom olika statesen som vårat fiske spela kommer anvämda
#vi har lagt dom för enkelhetens skull i kornologisk ordning
STATE_STANDING = "STATE_STANDING"
STATE_CASTING = "STATE_CASTING"
STATE_TREE = "STATE_TREE"
STATE_WAITING = "STATE_WAITING"
STATE_BITE = "STATE_BITE"
STATE_FIGHTING = "STATE_FIGHTING"
STATE_FIGHTING2 = "STATE_FIGHTING2"
STATE_FIGHTING3 = "STATE_FIGHTING3"
STATE_CATCHING = "STATE_CATCHING"
STATE_LOST = "STATE_LOST"
STATE_VICTORY = "STATE_VICTORY"
STATE_DEFEAT = "STATE_DEFEAT"
STATE_ENDING = "STATE_ENDING"
STATE_THEEND = "THEEND"

#här har vi använt os av FSM behaviour för hålla kolla så att agenten slutar och börjar i rätt states under uppbyggnad
#av spelet
class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()


#våran första state som har olika print för att ge känslan av en "historia" av en fiskedag
# vi använder en simpel input parameter samt en ifsats så användaren kan avgör om den vill fiska idag eller
#vänta till nästa dag
#vi använder os av asyncio sleep för att allting inte ska printas ut på en och samma gång, dettaa ger lite
#pauser så att den känns som en "historia"
#beroende på input användaren slussen den vidare till antingen kast staten eööer samma
class StateStanding(State):
    async def run(self):
        print("I'm standing at the lake on a beautiful day")
        await asyncio.sleep(3)
        print("do you wan to fish? yes or no")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_CASTING)
        elif userinput == "no":
            print("Goes home for today and returns the next day")
            self.set_next_state(STATE_STANDING)

#vi använder samma principer som i förra staten men har lagt in en chans att man råkar kasta draget i ett träd
#detta gjorde vi genom att importera random modluen så vi på ett enkelt sätt kan slumpa en siffra mellan 0-1
class StateCasting(State):
    async def run(self):
        print("Casting out the lure")
        await asyncio.sleep(3)
        randomnumber = random.random()
        if randomnumber < 0.1:
            print("you casted in to a tree and the lure was lost")
            self.set_next_state(STATE_TREE)
        else:
            self.set_next_state(STATE_WAITING)
#om man fastnar i ett träd får använder en möjlighet om den vil gör ett nytt försök
# och sätta på ett nytt drag eller om den vill sluta fiska för dagen, då slussen den till "förlust" state
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
        await asyncio.sleep(3)
        self.set_next_state(STATE_BITE)

class StateBite(State):
    async def run(self):
        print("A Fish Bites!")
        await asyncio.sleep(3)
        randomnumber = random.random()
        fish=""
        if randomnumber < 0.2:
            print("you have hooked a insanely huge pike")
            fish="pike"
            self.set_next_state(STATE_FIGHTING)
            self.agent.set("fish", fish)
        elif 0.2 <= randomnumber < 0.5:
            print("you have hooked a big perch")
            fish = "perch"
            self.set_next_state(STATE_FIGHTING)
            self.agent.set("fish", fish)
        elif randomnumber > 0.5:
            print("you have hooked a tiny roach")
            fish = "roach"
            self.set_next_state(STATE_FIGHTING)
            self.agent.set("fish", fish)



class StateFighting(State):
    async def run(self):

        hookedfish = self.agent.get("fish")
        print("you begin fighting the " + hookedfish)
        print(f"The {hookedfish} is fighting back hard!!")
        await asyncio.sleep(2)
        # vi använder random module
        # ett event av ovisshet för fiskaren, precis som i riktiga livet.
        print(f"\nThe {hookedfish} is trying to escape into the weeds!")
        await asyncio.sleep(3)
        print("Do you want to put MAX PRESSURE on the fish? (yes/no)")
        print("(YES = 50% chance to catch, but risk of line snap)")
        print("(NO  = 50% chance to catch, playing it safe but fish might escape)")
        #Sparar vi userinput
        userInput = input("Write yes or no: ").lower()
        randomnumber = random.random()
        winningword = ""

        if randomnumber >= 0.5:
            winningword = "yes"

        else:
            winningword = "no"

        if winningword == "yes" and userInput == "yes":
            print(f"Smart choice friend, putting more pressure on the {hookedfish}")
            self.agent.set("yes", winningword)
            await asyncio.sleep(2)
            self.set_next_state(STATE_FIGHTING2)
        elif winningword == "no" and userInput == "no":
            print(f"Coward choice but efficient, releasing pressure on {hookedfish}")
            self.agent.set("no", winningword)
            await asyncio.sleep(2)
            self.set_next_state(STATE_FIGHTING2)
        else:
            print("Noooo the fish was lost!!!!")
            await asyncio.sleep(2)
            self.set_next_state(STATE_LOST)


class StateFighting2(State):
    async def run(self):
        hookedfish = self.agent.get("fish")
        print("ROUND 2")
        await asyncio.sleep(2)
        print(f"\nThe {hookedfish} is getting tired and makes a run again!")
        await asyncio.sleep(3)
        print("Do you want to put PRESSURE on the fish? (yes/no)")
        print("(YES = 50% chance to catch, but risk of line snap)")
        print("(NO  = 50% chance to catch, playing it safe but fish might escape)")

        randomnumber = random.random()


        if randomnumber >= 0.5:
            winningword = "yes"
        else:
            winningword = "no"

        userInput = input("Write yes or no: ").lower()

        if winningword == "yes" and userInput == "yes":
            print("great move! you pulled the fish closer!")
            await asyncio.sleep(2)
            self.set_next_state(STATE_FIGHTING3)
        elif winningword == "no" and userInput == "no":
            print("Smart patience! The fish stopped running")
            await asyncio.sleep(2)
            self.set_next_state(STATE_FIGHTING3)
        else:
            print(f"WRONG MOVE! The {hookedfish} jumped and spit the hook!")
            await asyncio.sleep(2)
            self.set_next_state(STATE_LOST)

class StateFighting3(State):
    async def run(self):
        hookedfish = self.agent.get("fish")
        print(f"\nROUND 3 FINAL")
        await asyncio.sleep(2)
        print(f"The {hookedfish} is by the shore close to us! ")
        await asyncio.sleep(3)
        print("Do you want to force it to the net? (yes/no)")
        userInput = input("Write yes or no: ").lower()
        randomnumber = random.random()
        winningword = ""

        if randomnumber >= 0.5:
            winningword = "yes"
        else:
            winningword = "no"

        if winningword == "yes" and userInput == "yes":
            print("GOTCHA!! Into the net it goes")
            await asyncio.sleep(2)
            self.set_next_state(STATE_CATCHING)
        elif winningword == "no" and userInput == "no":
            print("Slow and smooth, gently gliding it in")
            await asyncio.sleep(2)
            self.set_next_state(STATE_CASTING)
        else:
            print("SNAP, oh my god lost it in the end....")
            await asyncio.sleep(2)
            self.set_next_state(STATE_LOST)


class StateLost(State):
    async def run(self):
        print("The fish was lost")
        await asyncio.sleep(3)
        print("feeling like the worst fisherman in history")
        self.set_next_state(STATE_DEFEAT)


class StateCatching(State):
    async def run(self):
        hookedfish = self.agent.get("fish")
        print(f"Catch personal best {hookedfish} and cries a little")
        await asyncio.sleep(3)
        self.set_next_state(STATE_VICTORY)

class StateVictory(State):
    async def run(self):
        print("Celebrates catching the fish of a lifetime with a cold beer")
        await asyncio.sleep(3)
        print("you leave the lake as a happy angler")
        self.set_next_state(STATE_ENDING)

class StateDefeat(State):
    async def run(self):
        await asyncio.sleep(3)
        print("you full of sadness and thoughts of selling your'e fishing gear enters your mind")
        await asyncio.sleep(3)
        print("you leave the lake as a broken man")
        self.set_next_state(STATE_ENDING)

class StateEnding(State):
    async def run(self):
        print("do you want to fish the next day as well? write: yes  or are you satisfied for the moment? write: no ")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_STANDING)
        elif userinput == "no":
            self.set_next_state(STATE_THEEND)

class StateTheEnd(State):
    async def run(self):
        print("thanks for playing Fishing day")

class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_STANDING, state=StateStanding(), initial=True)
        fsm.add_state(name=STATE_CASTING, state=StateCasting())
        fsm.add_state(name=STATE_TREE, state=StateTree())
        fsm.add_state(name=STATE_WAITING, state=StateWaiting())
        fsm.add_state(name=STATE_BITE, state=StateBite())
        fsm.add_state(name=STATE_FIGHTING, state=StateFighting())
        fsm.add_state(name=STATE_FIGHTING2, state=StateFighting2())
        fsm.add_state(name=STATE_FIGHTING3, state=StateFighting3())
        fsm.add_state(name=STATE_CATCHING, state=StateCatching())
        fsm.add_state(name=STATE_VICTORY, state=StateVictory())
        fsm.add_state(name=STATE_LOST, state=StateLost())
        fsm.add_state(name=STATE_DEFEAT, state=StateDefeat())
        fsm.add_state(name=STATE_ENDING, state=StateEnding())
        fsm.add_state(name=STATE_THEEND, state=StateTheEnd())
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
        fsm.add_transition(source=STATE_FIGHTING, dest=STATE_FIGHTING2)
        fsm.add_transition(source=STATE_FIGHTING2, dest=STATE_LOST)
        fsm.add_transition(source=STATE_FIGHTING2, dest=STATE_FIGHTING3)
        fsm.add_transition(source=STATE_FIGHTING3, dest=STATE_LOST)
        fsm.add_transition(source=STATE_FIGHTING3, dest=STATE_CATCHING)
        fsm.add_transition(source=STATE_CATCHING, dest=STATE_VICTORY)
        fsm.add_transition(source=STATE_LOST, dest=STATE_DEFEAT)
        fsm.add_transition(source=STATE_VICTORY, dest=STATE_ENDING)
        fsm.add_transition(source=STATE_DEFEAT, dest=STATE_ENDING)
        fsm.add_transition(source=STATE_ENDING, dest=STATE_STANDING)
        fsm.add_transition(source=STATE_ENDING, dest=STATE_THEEND)
        self.add_behaviour(fsm)


async def main():
    fsmagent = FSMAgent("h23patpe@conversations.im", "Jhgblo10")
    await fsmagent.start()
    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())