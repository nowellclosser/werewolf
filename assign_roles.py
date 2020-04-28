import os
import json
import random
import math

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
# ONE_OF_THE_TWO_SISTERS = 'One of the Two Sisters'
RAVEN = 'Raven'
SCAPEGOAT = 'Scapegoat'

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
    # ONE_OF_THE_TWO_SISTERS,
    RAVEN,
    SCAPEGOAT,
]

ROLE_DESCRIPTIONS = {
    WEREWOLF: 'You are a plain werewolf. You will be woken up by the moderator each night with all living werewolves and decide on someone to kill (possibly a werewolf). Your goal is to eliminate all villagers.',
    VILLAGER: 'You are a plain villager, whose only responsibility is to participate in the daily town meeting. Your goal is to eliminate all werewolves.',
    DOCTOR: 'You are a villager, but you will be woken up alone by the moderator each night and pick one person (possibly yourself) to protect. If that person is targeted by the werewolves that night, they will not die. Your goal is to eliminate all werewolves.',
    WITCH: 'You are a villager, but you will be woken up alone by the moderator each night and choose to save someone and/or kill someone. However, you can do each of those only once per game. Your kill cannot be prevented by the doctor.  Your goal is to eliminate all werewolves.',
    HUNTER: 'You are a villager, but whenever you die, whether night or day, you must choose a second person to die with you, with no discussion. Your goal is to eliminate all werewolves.',
    FORTUNE_TELLER: 'You are a villager, but you will be woken up alone by the moderator each night and choose someone to inspect.  The moderator will indicate whether that person is a werewolf. Your goal is to eliminate all werewolves.',
    ANCIENT: 'You are a villager, who will not die the first time the werewolves target you.  However, if any villager, like the Witch, kills you, or the townspeople vote to kill you, all villagers lose their powers.',
    ACTOR: 'You are a villager, but the moderator has chosen three other special roles for you, all unknown to you.  Each night, you will be woken up by the moderator and can elect to randomly receive one of those roles, to be used until the following night.  However, a role is used up once you receive it, so you can use your power a maximum of three times.',
    STUTTERING_JUDGE: 'You are a villager. One time during the game, you may secretly signal to the moderator that a second discussion and vote should be held immediately afterward, to kill a second person.',
    # ONE_OF_THE_TWO_SISTERS: 'You are a villager, but you will be shown the identity of your sister, who is also a villager, allowing you two to trust each other.',
    RAVEN: 'You are a villager.  Each night, the moderator will wake you up and ask who you would like to curse with two votes for the following day. You may not curse yourself.',
    SCAPEGOAT: 'You are a villager. In the event that voting ever results in a tie when you are alive, you die and voting for the round ends. However, your revenge, if you die this way, is that you choose someone to not be allowed to vote the following day.',
    BIG_BAD_WEREWOLF: 'You are a werewolf, but an extremely powerful one.  As long as no werewolves have been eliminated, the moderator will wake you up a second time at night, alone, and you will choose another player to kill.',
    CURSED_WOLF_FATHER: 'You are a werewolf with a special twist. One time during the game, you may secretly signal to the moderator that the target you and the other werewolves picked to kill will become a werewolf instead of dying.',
}

# Notes for moderator about who has to wake up and things to keep track of?

assert len(ROLE_DESCRIPTIONS) == len(STANDARD_SPECIAL_VILLAGERS) + len(ADVANCED_SPECIAL_VILLAGERS) + len(SPECIAL_WEREWOLVES) + 2

WEREWOLF_CHANNEL_ID = 'C011ANJ5X17'


def get_boolean_input(prompt, help_label=None, help_text=None):
    while True:
        options = ' y/n\n' if not (help_label and help_text) else f' y/n/{help_label}\n'
        raw = input(prompt + options).lower()
        if help_label and help_text and raw == help_label:
            print('\n{}\n'.format(help_text))
            continue
        if raw not in {'y', 'n'}:
            print(f"Only 'Y', 'y', 'N', and 'n' and {help_label} are valid inputs. Please try again.")
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


def get_informative_name(client, member_id):
    player_info = client.users_info(user=member_id)
    if player_info.data['user']['is_bot']:
        return
    display_name = (player_info.data['user']['profile']['display_name']
        or player_info.data['user']['name'])
    real_name = player_info.data['user']['profile']['real_name']

    return f'@{display_name} ({real_name})'



def main():
    client = WebClient(token=API_TOKEN)

    # Determine which members of the #werewolf channel are playing
    print("Welcome to Werewolf!\n")
    print("Let's select the active players. Gathering potential player information from Slack...\n")
    player_candidates = client.conversations_members(
        channel=WEREWOLF_CHANNEL_ID
    )

    moderator_id = None
    while not moderator_id:
        raw = input("Please give the member ID of the moderator. This looks like U15EACZKP and can be found on their profile.\n")
        if raw not in player_candidates.data['members']:
            print("That member id is not found in the channel. Try again.")
            continue
        print(f"Ok, {get_informative_name(client, raw)} will be the moderator.\n")
        moderator_id = raw

    active_players = {}
    for member_id in player_candidates.data['members']:
        if member_id == moderator_id:
            continue

        # get rid of?
        informative_name = get_informative_name(client, member_id)
        if not informative_name: # This means bot
            continue
        # ask if you want all players in channel?
        if get_boolean_input(f'Is {informative_name} playing?'):
            active_players[member_id] = informative_name

    num_players = len(active_players)

    if get_boolean_input(f"Great. You have {num_players} players. Would you like a summary of all possible roles?"):
        print(json.dumps(ROLE_DESCRIPTIONS, indent=4))

    roles = []
    special_werewolves = []
    if get_boolean_input('Ok, time to configure the werewolves. Would you like to use special werewolves?'):
        for role in SPECIAL_WEREWOLVES:
            if get_boolean_input(
                    f'Would you like to include the {role}?',
                    help_label='desc',
                    help_text=ROLE_DESCRIPTIONS[role]
            ):
                special_werewolves.append(role)

    roles += special_werewolves
    num_special_wolves = len(special_werewolves)
    max_num_werewolves = (num_players - 1) // 2
    num_plain_wolves = get_int_input(
        f'How many normal werewolves (between {int(not num_special_wolves)} and {max_num_werewolves - num_special_wolves}) would you like in addition to the {num_special_wolves} special one(s)?',
        lower_bound=int(not num_special_wolves),
        upper_bound=max_num_werewolves - num_special_wolves
    )
    num_wolves = num_plain_wolves + num_special_wolves
    num_villagers = num_players - num_wolves
    print(f"Ok. You have chosen {num_plain_wolves} plain werewolves and {num_special_wolves} special werewolves, leaving {num_villagers} villagers. Let's configure the villagers.")


    possible_special_villagers = STANDARD_SPECIAL_VILLAGERS
    if get_boolean_input('Would you like to use advanced special villagers?'):
        possible_special_villagers += ADVANCED_SPECIAL_VILLAGERS

    special_villagers = []
    for role in possible_special_villagers:
        if len(special_villagers) < num_villagers and get_boolean_input(
                f'Would you like to include the {role}?',
                help_label='desc',
                help_text=ROLE_DESCRIPTIONS[role]
        ):
            special_villagers.append(role)

        print(f'{num_villagers - len(special_villagers)} unassigned villagers remaining.\n')

    roles += special_villagers

    if len(special_villagers) == num_villagers:
        print('All available villagers have been made special. Stopping configuration')

    print(f'Ok, you have the following special villager roles: {special_villagers}.\n')

    # Angels and demons?
    print(f'Configuration complete. Sending roles.')

    roles += [WEREWOLF] * num_wolves
    roles += [VILLAGER] * (num_players - len(roles))
    random.shuffle(roles)

    assigned_roles = {}
    for idx, member_id in enumerate(active_players):
        assigned_role = roles[idx]
        assigned_roles[member_id] = assigned_role
        # Get rid of summary?
        summary_text = f'You are in a town of {num_players} members, of which {num_wolves} are werewolves. Everyone else is a villager, including the following special member(s): {special_villagers}.'
        role_text = f'Your role is *{assigned_role}*: {ROLE_DESCRIPTIONS[assigned_role]}'
        player_message = '\n'.join([summary_text, role_text, 'Good luck!'])

        # Should go to player
        client.chat_postMessage(
            channel='D012RG18RGU',
            text=player_message,
            as_user=True
        )

    # Should go to moderator
    all_roles = '\n'.join([f'<@{mid}>: *{assigned_roles[mid]}*' for mid in active_players])
    client.chat_postMessage(
        channel='D012RG18RGU',
        text=f'All roles:\n {all_roles}',
        as_user=True
    )

    # Should go to werewolf channel
    player_summary = '\n'.join([f'<@{mid}>' for mid in active_players])

    role_summary_header= f'We will begin with *{num_wolves}* werewolves and *{num_villagers}* villagers, including the following special roles:\n'
    special_roles_text = '\n'.join(f'\n*{role}*: {ROLE_DESCRIPTIONS[role]}' for role in (special_villagers + special_werewolves))
    client.chat_postMessage(
        channel='D012RG18RGU',
        text=f"Starting a game, moderated by <@{moderator_id}>, with\n {player_summary}.\n {role_summary_header}{special_roles_text}",
        as_user=True
    )

    # Start group chat with moderator and werewolves?

if __name__ == '__main__':
    main()


