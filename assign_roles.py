import os
import json
import random

from slack import WebClient

API_TOKEN = os.environ['SLACK_API_TOKEN']

WEREWOLF = 'Werewolf'

VILLAGER = 'Villager'
DOCTOR = 'Doctor'
WITCH = 'Witch'
HUNTER ='Hunter'
FORTUNE_TELLER = 'Fortune Teller'

BIG_BAD_WEREWOLF = 'Big Bad Wolf'
CURSED_WOLF_FATHER = 'Cursed Wolf-Father'

ANCIENT = 'Ancient'
ACTOR = 'Actor'
STUTTERING_JUDGE = 'Stuttering Judge'
ONE_OF_THE_TWO_SISTERS = 'One of the Two Sisters'
RAVEN = 'Raven'
SCAPEGOAT_NO_REVENGE = 'Scapegoat With No Revenge'
SCAPEGOAT_REVENGE = 'Scapegoat With Revenge'
BUSY_DOCTOR = 'Busy Doctor'

STANDARD_SPECIAL_VILLAGERS = [
    DOCTOR,
    WITCH,
    HUNTER,
    FORTUNE_TELLER
]

SPECIAL_WEREWOLVES = [
    BIG_BAD_WEREWOLF,
    CURSED_WOLF_FATHER
]

ADVANCED_SPECIAL_VILLAGERS = [
    ANCIENT,
    ACTOR,
    STUTTERING_JUDGE,
    ONE_OF_THE_TWO_SISTERS,
    RAVEN,
    SCAPEGOAT_NO_REVENGE,
    SCAPEGOAT_REVENGE,
    BUSY_DOCTOR
]

ROLE_DESCRIPTIONS = {
    WEREWOLF: 'You are a plain werewolf. You will be woken up by the moderator each night with all living werewolves and decide on someone to kill (possibly a werewolf). Your goal is to eliminate all villagers.',
    BIG_BAD_WEREWOLF: 'You are a werewolf, but an extremely powerful one.  As long as no werewolves have been eliminated, you wake up alone a second time at night and choose another player to kill.',
    CURSED_WOLF_FATHER: 'You are a werewolf with a special twist. One time during the game, you may secretly signal to the moderator that the target you and the other werewolves picked to kill will instead become a werewolf.',
    VILLAGER: 'You are a plain villager, whose only responsibility is to participate in the daily town meeting. Your goal is to eliminate all werewolves.',
    DOCTOR: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person (possibly yourself) to protect. If that person is targeted by the werewolves that night, they will not die. Your goal is to eliminate all werewolves.',
    WITCH: 'You are a villager, but you will be woken up alone by the moderator each night and choose to save someone and/or kill someone. However, you can do each of those only once per game. Your kill cannot be prevented by the doctor.  Your goal is to eliminate all werewolves.',
    HUNTER: 'You are a villager, but whenever you die, whether night or day, you must choose a second person to die with you, with no discussion. Your goal is to eliminate all werewolves.',
    FORTUNE_TELLER: 'You are a villager, but you will be woken up alone by the moderator each night and choose someone to inspect.  The moderator will indicate whether that person is a werewolf. Your goal is to eliminate all werewolves.',
    ANCIENT: 'You are a villager, who will not die the first time the werewolves target you.  However, if any villager like the Witch kills you, or the townspeople vote to kill you, they all lose their powers.',
    ACTOR: 'You are a villager, but the moderator has chosen three other special roles for you, all unknown to you.  Each night, you will be woken up by the moderator and can elect to randomly receive one of those roles, to be used until the following night.  However, a role is used up once you receive it, so you can use your power a maximum of three times.',
    STUTTERING_JUDGE: 'You are a villager. One time during the game, you may secretly signal to the moderator that a second discussion and vote should be held immediately afterward, to kill a second person.',
    ONE_OF_THE_TWO_SISTERS: 'You are a villager, but you will be shown the identity of your sister, who is also a villager, allowing you two to trust each other.',
    RAVEN: 'You are a villager.  Each night, the moderator will wake you up and ask who you would like to curse with two votes for the following day.',
    SCAPEGOAT_NO_REVENGE: 'You are a villager.  In the event that voting ever results in a tie, you die and the round is over.',
    SCAPEGOAT_REVENGE: 'You are a villager. In the event that voting ever results in a tie, you die and voting for the round ends. However, your revenge, if you die this way, is that you may (in fact must) choose someone that will not be allowed to vote the following day.',
    BUSY_DOCTOR: 'You are a villager.  You are like a normal doctor, choosing someone to protect each night, but you cannot protect the same person two nights in a row',
}

# Notes for moderator about who has to wake up and other things?

assert len(ROLE_DESCRIPTIONS) == len(STANDARD_SPECIAL_VILLAGERS) + len(ADVANCED_SPECIAL_VILLAGERS) + len(SPECIAL_WEREWOLVES) + 2

WEREWOLF_CHANNEL_ID = 'C011ANJ5X17'


def get_boolean_input(prompt, help_label=None, help_text=None):
    while True:
        options = ' y/n\n' if not (help_label and help_text) else f' y/n/{help_label}\n'
        raw = input(prompt + options).lower()
        if help_label and help_text and raw == help_label:
            print(help_text)
            continue
        if raw not in {'y', 'n'}:
            print("Only 'Y', 'y', 'N', and 'n' are valid inputs. Please try again.")
            continue

        return raw == 'y'


def get_int_input(prompt, lower_bound=0, upper_bound=float('+inf')):
    while True:
        try:
            result = int(input(prompt + '\n'))
            assert lower_bound <= result <= upper_bound
            return result
        except (AssertionError, ValueError):
            print(f"Couldn't interpret input as an integer between {lower_bound} and {upper_bound}. Please try again.")


def main():
    # This token should be that of the werewolf-roles bot
    client = WebClient(token=API_TOKEN)

    # Determine which members of the #werewolf channel are playing
    print("Gathering player information...")
    player_candidates = client.conversations_members(
        channel=WEREWOLF_CHANNEL_ID
    )

    active_players = {}
    moderator_id = None
    for member_id in player_candidates.data['members']:
        if member_id == moderator_id:
            continue

        player_info = client.users_info(user=member_id)
        if player_info.data['user']['is_bot']
            continue

        display_name = (player_info.data['user']['profile']['display_name']
            or player_info.data['user']['name'])
        real_name = player_info.data['user']['profile']['real_name']

        informative_name = f'@{display_name} (~{real_name}~)'

        if not moderator_id and get_boolean_input(f'Is {informative_name} the moderator?'):
            moderator_id = member_id
        elif get_boolean_input(f'Are they playing?'):
            active_players[informative_name] = member_id

    if not moderator_id:
        raise InputError("Sorry, you forgot to select a moderator.")

    num_players = len(active_players)

    if get_boolean_input()

    possible_special_villagers = STANDARD_SPECIAL_VILLAGERS
    if get_boolean_input('Would you like to consider using advanced special villagers?'):
        possible_special_villagers += ADVANCED_SPECIAL_VILLAGERS


    special_villagers = []
    for role in possible_special_villagers:
        if get_boolean_input(
                f'Would you like to include a {role}?',
                help_label='desc',
                help_text=ROLE_DESCRIPTIONS[role]
        ):
            special_villagers.append(role)

    roles = list(special_villagers)

    print(f'Ok, you have {num_players} players, and the following special villager roles: {special_villagers}.')

    special_werewolves = []
    if get_boolean_input('Would you like to include special werewolves?'):
        for role in SPECIAL_WEREWOLVES:
            if get_boolean_input(
                    f'Would you like to include a {role}?',
                    help_label='desc',
                    help_text=ROLE_DESCRIPTIONS[role]
            ):
                special_werewolves.append(role)

    roles += special_werewolves
    num_special_wolves = len(special_werewolves)

    max_num_werewolves = num_players // 2 - 1
    num_plain_wolves = get_int_input(
        f'How many non-special werewolves (between {min(1, num_special_wolves)} and, say, {max_num_werewolves - num_special_wolves}) would you like?',
        lower_bound=1,
        upper_bound=max_num_werewolves
    )
    num_wolves = num_plain_wolves + num_special_wolves

    print(f'Ok, starting game with {num_plain_wolves} plain werewolves and {num_special_wolves} special wolves. Sending roles now.')

    roles += [WEREWOLF] * num_wolves
    roles += [VILLAGER] * (num_players - len(roles))
    random.shuffle(roles)

    assigned_roles = {}
    for idx, (name, member_id) in enumerate(active_players.items()):
        assigned_role = roles[idx]
        assigned_roles[name] = assigned_role
        summary_text = f'You are in a town of {num_players} members, of which {num_wolves} are werewolves. Everyone else is a villager, including the following special members: {special_villagers}.'
        role_text = f'Your role is *{assigned_role}*. {ROLE_DESCRIPTIONS[assigned_role]}'
        player_message = '\n'.join([summary_text, role_text, 'Good luck!'])

        # Should go to player
        client.chat_postMessage(
            channel='D012RG18RGU',
            text=player_message,
            as_user=True
        )

    # Should go to moderator
    client.chat_postMessage(
        channel='D012RG18RGU',
        text=f'All roles: {json.dumps(assigned_roles, indent=4)}',
        as_user=True
    )

    # Should go to werewolf channel
    client.chat_postMessage(
        channel='D012RG18RGU',
        text=f'Starting a game with {json.dumps(list(active_players.keys()), indent=4)}',
        as_user=True
    )

    # Start group chat with moderator and werewolves?
if __name__ == '__main__':
    main()


