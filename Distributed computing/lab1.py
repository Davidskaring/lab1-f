from enum import nonmember

import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
import random
import asyncio
from spade.message import Message

#here we declare the different states we will use in our fishing game
# for the simplicity we put the states in chronological order
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

#here vi declare the FSMBehavour from spade, we also use diffrenet prints to keep track of what state it start in and
#what state it ends in.
#this has been benefical for us during coding if we encounter a code fault and so forf
class AgentFSMBehaviour(FSMBehaviour):
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
#here is our first state which has multiple prints to give the feeling of a "story" of a fishing day
# we use a simple input parameter and a if statement so the user can choose if they want to fish this day or not.
#we use asyncio sleep so every print is not printed at the exact same time to give a "storytelling" feeling
# depending on the choice of the user(input) they either transition to the next state or are go back to beginning of this
#state again
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

#We are using the same syntax/principles from the last state but we have added a state were you can accidently throw the lure into a tree
#we did this nu importing the random module so that we could easily implement the logic of randomising a float number between 0 and 1
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
#If u get stuck in a tree you'll get the opportunity to try casting again
#and to put on a new lure or if the user wants to quit the fishing game for the day, then it will move on to STATE_LOST
class StateTree(State):
    async def run(self):
        print("do you want to put on a new lure and trying again? yes or no")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_CASTING)
        elif userinput == "no":
            self.set_next_state(STATE_DEFEAT)


#this state represent the moment of wating on the fish to bite
#much like it is in real life fishing
#this state basicically act as an transistion state and just adds to the "story" of the game
class StateWaiting(State):
    async def run(self):
        print("I'm waiting for a fish to bite")
        await asyncio.sleep(3)
        self.set_next_state(STATE_BITE)

# Here we begin the main act of the games "story" where the fish is biting
#we have apply the random module here to make a element of surprise in what fish can bite
class StateBite(State):
    async def run(self):
        print("A Fish Bites!")
        await asyncio.sleep(3)
        randomnumber = random.random()
        fish=""
        if randomnumber < 0.2:
            print("you have hooked a insanely huge pike")
            print(randomnumber)
            fish="pike"
            self.set_next_state(STATE_FIGHTING)
            self.agent.set("fish", fish)
        elif 0.2 <= randomnumber < 0.5:
            print("you have hooked a big perch")
            print(randomnumber)
            fish = "perch"
            self.set_next_state(STATE_FIGHTING)
            self.agent.set("fish", fish)
        elif randomnumber > 0.5:
            print("you have hooked a tiny roach")
            print(randomnumber)
            fish = "roach"
            self.set_next_state(STATE_FIGHTING)
            #a intresting thing we here is from the spade agent module whihch self.agent.set() method
            #gives us an option to store the fishes namne which is a knowledge item in this case in the agents knowlegde base.
            self.agent.set("fish", fish)


# This class implements the core gameplay mechanic: the struggle between the angler and the fish.
# It handles user input, random probability and state transitions based on the outcome.
class StateFighting(State):
    async def run(self):
        # Retrieve the specific fish object/string from the agent's Knowledge Base.
        # This ensures continuity from the previous state (ex we fight the same fish we hooked).
        hookedfish = self.agent.get("fish")
        print("you begin fighting the " + hookedfish)
        print(f"The {hookedfish} is fighting back hard!!")
        await asyncio.sleep(2)


        # Here is the user decesion phase
        # We present the user with a tactical choice.
        # This adds an element of agency and strategy to the simulation.
        # vi använder random module
        # ett event av ovisshet för fiskaren, precis som i riktiga livet.
        print(f"\nThe {hookedfish} is trying to escape into the weeds!")
        await asyncio.sleep(3)
        print("Do you want to put MAX PRESSURE on the fish? (yes/no)")
        print("(YES = 50% chance to catch, but risk of line snap)")
        print("(NO  = 50% chance to catch, playing it safe but fish might escape)")
        #Here is the probability engine
        #We use the random module to simulate the unoredictible nature of fishing.
        # This determines what the correct action would have been for this specific event.
        userInput = input("Write yes or no: ").lower()
        randomnumber = random.random()
        winningword = ""

        # Determine the winning condation base on a 50/50 probability
        if randomnumber >= 0.5:
            winningword = "yes" # In this scenario, aggression (Max Pressure) was the right call.

        else:
            winningword = "no" # In this scenario, patience (Playing Safe) was the right call.

        # Here is our outcome evaluation
        # We compare the users inout against the randomized winning condition
        # First scenario: The user chose the aggresive play and it was the correct move.
        if winningword == "yes" and userInput == "yes":
            print(f"Smart choice friend, putting more pressure on the {hookedfish}")
            print(randomnumber)
            # Here we store the succesful move in the agents memory for future reference.
            self.agent.set("yes", winningword)
            await asyncio.sleep(2)
            # Here we proceed to the next stage of the fight.
            self.set_next_state(STATE_FIGHTING2)
            # Scenario 2: The user chose passive action and it was the correct move.
        elif winningword == "no" and userInput == "no":
            print(f"Coward choice but efficient, releasing pressure on {hookedfish}")
            print(randomnumber)
            # Store the successful move.
            self.agent.set("no", winningword)
            await asyncio.sleep(2)
            # Proceed to next step of the game
            self.set_next_state(STATE_FIGHTING2)
        else: # Scenario 3: The user's choice did not match the random event (Failure).
            print("Noooo the fish was lost!!!!")
            await asyncio.sleep(2)
            self.set_next_state(STATE_LOST)


class StateFighting2(State):
    async def run(self):
        # Retrieve the specific fish object/string from the agent's Knowledge Base.
        # This ensures continuity from the previous state (ex we fight the same fish we hooked).
        hookedfish = self.agent.get("fish")
        print("ROUND 2")
        await asyncio.sleep(2)
        print(f"\nThe {hookedfish} is getting tired and makes a run again!")
        await asyncio.sleep(3)
        print("Do you want to put PRESSURE on the fish? (yes/no)")
        print("(YES = 50% chance to catch, but risk of line snap)")
        print("(NO  = 50% chance to catch, playing it safe but fish might escape)")

        # We use the random module to simulate the unpredictable nature of fishing.
        # This determines what the correct action would have been for this specific event.
        randomnumber = random.random()

        # Determine the winning condation based on a 50/50 probability
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
        # Retrieve the specific fish object/string from the agent's Knowledge Base.
        # This ensures continuity from the previous state (ex we fight the same fish we hooked).
        hookedfish = self.agent.get("fish")
        print(f"\nROUND 3 FINAL")
        await asyncio.sleep(2)
        print(f"The {hookedfish} is by the shore close to us! ")
        await asyncio.sleep(3)
        print("Do you want to force it to the net? (yes/no)")
        userInput = input("Write yes or no: ").lower()
        # We use the random module to simulate the unpredictable nature of fishing.
        # This determines what the correct action would have been for this specific event.
        randomnumber = random.random()
        winningword = ""

        # Determine the winning condation based on a 50/50 probability
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
            self.set_next_state(STATE_CATCHING)
        else:
            print("SNAP, oh my god lost it in the end....")
            await asyncio.sleep(2)
            self.set_next_state(STATE_LOST)

# This state represents the immediate aftermath of losing the fish.
# It acts as a transitional state between the gameplay failure and the final stages of our game.
class StateLost(State):
    async def run(self):
        print("The fish was lost")
        await asyncio.sleep(3)
        print("feeling like the worst fisherman in history")
        self.set_next_state(STATE_DEFEAT)


# This state represents the climax of the fishing event where the player successfully lands the fish.
# It retrieves the specific fish type stored in the agent's memory to personalize the success message.
class StateCatching(State):
    async def run(self):
        # Retrieve the specific fish type from the Knowledge Base
        # to confirm exactly what the player caught.
        hookedfish = self.agent.get("fish")
        print(f"Catch personal best {hookedfish} and cries a little")
        await asyncio.sleep(3)
        self.set_next_state(STATE_VICTORY)

# This state handles the final stage in the game.
# It serves as the final celebration phase before the agent finishes its lifecycle
class StateVictory(State):
    async def run(self):
        print("Celebrates catching the fish of a lifetime with a cold beer")
        await asyncio.sleep(3)
        print("you leave the lake as a happy angler")
        self.set_next_state(STATE_ENDING)

# This class represents the "Defeat" state.
# The agent enters this state when the player fails to catch the fish.
class StateDefeat(State):
    async def run(self):
        await asyncio.sleep(3)
        print("you full of sadness and thoughts of selling your'e fishing gear enters your mind")
        await asyncio.sleep(3)
        print("you leave the lake as a broken man")
        self.set_next_state(STATE_ENDING)

#Here we create a state called StateEnding that the agent calls upon when finishing the game but
#gives some questions to the user before going to another state. If the user wants to play more he types in yes, or
# else no. These states have different paths to go from aswell
class StateEnding(State):
    async def run(self):
        print("do you want to fish the next day as well? write: yes  or are you satisfied for the moment? write: no ")
        userinput = input()
        if userinput == "yes":
            self.set_next_state(STATE_STANDING)
        elif userinput == "no":
            self.set_next_state(STATE_THEEND)

#Here we create a state called stateTheEnd that the agent calls upon when finishing the game
class StateTheEnd(State):
    async def run(self):
        print("thanks for playing Fishing day")

class FSMAgent(Agent):
    async def setup(self):
        # Here we create our fsm behavior object (the container)
        fsm = AgentFSMBehaviour()
        # Here is were we add all our states in the FSMAgent class were we first create an object fsm to later on
        # implement and create our different states.
        # We instaciate our state classes (like StateStanding) and register them to an FSM agent so the agent knows
        # which state that exists.
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

        # Here is our transitions, were one state can go to another state.
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

#Here is our main program were we fire up our agent, and delegating the agent an server.
async def main():
    fsmagent = FSMAgent("h23patpe@conversations.im", "Jhgblo10")
    await fsmagent.start()
    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())